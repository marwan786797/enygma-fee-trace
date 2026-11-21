"""Fresh, out-of-sample check straight from the public Rayls testnet RPC. Reads NO saved file from this pack.
It takes every Enygma Public fee paid AFTER my snapshot block (24,667,602, 20 Nov 2026 09:41:12 UTC), so fees
I had never looked at when I wrote the formula down, and for each one checks:
  1. formula: fee == (req.gas + 150000 + 16 x (calldata + 700) [+100000 with a token fee]) x 2.4e12 wei x 115/100
     (req.gas and calldata come from the signed request inside the tx input)
  2. commission: a separate RLS transfer relayer -> 0x71AF of exactly floor(fee x 15/115) within 600 blocks
It also lists every relayer -> 0x71AF RLS payout in the window (that includes payouts for fees paid privately
from shielded RLS, which by design have no public fee to match).
Run: python fresh_check.py [--from-block N] [--to-block N] [--self-test]     Output: stdout + evidence/fresh_check_<to_block>.json
--self-test is a negative control: it moves the price by 1 wei per gas and the expected payout by 1 wei, so every check
must fail. If it still says "exact", the checker is broken."""
import sys, json, os, collections
from eth_abi import decode
from common import rpc, fmt, times, txlink, RELAYED, TRANSFER, RELAYER, COMMISSION, RLS

FORWARDER = "0x12B6640048DEB2e8fFDa4Bc10Bb2a640B70eCA6d"
RLS_PER_GAS = 2_400_000_000_000      # fixed test price, 2.4 RLS per million gas (Rayls team, r/Rayls, 20 Nov 2026)
SELF_TEST = "--self-test" in sys.argv  # negative control: shift the price by 1 wei per gas and the payout by 1 wei, every check must fail
if SELF_TEST: RLS_PER_GAS += 1
SNAPSHOT = 24_667_602
MINE = {"0x4f1aa6cb2c8932583f2844a855fb057c589f23e9", "0x9d42151e47511d72dbbdd54824053a88f343d3e0", "0xd0a85b7571000c6f8dc89699bbcd69862f343c7d"}  # my 3 throwaway test accounts
arg = lambda k, d: int(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
LATEST = int(rpc("eth_blockNumber", []), 16)
FROM, TO = arg("--from-block", SNAPSHOT + 1), arg("--to-block", LATEST)
EXEC = ["(address,address,uint256,uint256,uint256,uint256,bytes)", "bytes", "(uint256,uint256,uint8,bytes32,bytes32)"]
topic = lambda a: "0x" + "0" * 24 + a.lower()[2:]

def logs(q):
    out, a = [], FROM
    while a <= TO:                                  # page in 50k block chunks
        b = min(a + 50_000, TO)
        out += rpc("eth_getLogs", [dict(q, fromBlock=hex(a), toBlock=hex(b))]); a = b + 1
    return out

def signed_request(h):
    inp = rpc("eth_getTransactionByHash", [h])["input"]
    if inp[:10] == "0x82ad56cb":                    # Multicall3 batch: pick the forwarder execute() call
        (calls,) = decode(["(address,bool,bytes)[]"], bytes.fromhex(inp[10:]))
        inp = "0x" + [c[2] for c in calls if c[2][:4].hex() == "e2076320"][0].hex()
    req, _, _ = decode(EXEC, bytes.fromhex(inp[10:]))
    return req[2], len(req[6])                      # req.gas, calldata bytes

fees = logs({"address": FORWARDER, "topics": [RELAYED]})
pays = logs({"address": RLS, "topics": [TRANSFER, topic(RELAYER), topic(COMMISSION)]})
byval = collections.defaultdict(list)
for p in pays: byval[int(p["data"], 16)].append(p)
used, rows = set(), []
for l in fees:
    fee = int(l["data"][2 + 64:2 + 128], 16); blk = int(l["blockNumber"], 16); h = l["transactionHash"]
    acct = "0x" + l["topics"][1][-40:]
    mine = acct.lower() in MINE
    if fee == 0:                                    # sponsored request: no fee charged, so nothing to price or pay out
        rows.append({"tx": txlink(h), "block": blk, "account": acct, "mine": mine, "fee_rls": "0", "formula": "n/a (fee 0, sponsored)",
                     "commission_rls": "0", "payout": None, "time": ""}); continue
    gas, n = signed_request(h)
    base = gas + 150_000 + 16 * (n + 700)
    f0, f1 = base * RLS_PER_GAS * 115 // 100, (base + 100_000) * RLS_PER_GAS * 115 // 100
    formula = "exact" if fee == f0 else "exact (+100,000 token fee gas)" if fee == f1 else f"no ({fmt(fee - f0)} RLS off)"
    want = fee * 15 // 115 + (1 if SELF_TEST else 0)
    m = next((p for p in byval[want] if p["transactionHash"] not in used and blk <= int(p["blockNumber"], 16) <= blk + 600), None)
    if m: used.add(m["transactionHash"])
    ts = int(rpc("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16)
    rows.append({"tx": txlink(h), "block": blk, "account": acct, "mine": mine, "time": " / ".join(times(ts)), "fee_rls": fmt(fee), "formula": formula,
                 "commission_rls": fmt(want), "payout": txlink(m["transactionHash"]) if m else None})
other = [p for p in pays if p["transactionHash"] not in used]
vals = collections.Counter(fmt(int(p["data"], 16)) for p in other)
paid = [r for r in rows if r["fee_rls"] != "0"]
res = {"rpc": "https://testnet-rpc.rayls.com", "from_block": FROM, "to_block": TO,
       "public_fee_events": len(rows), "sponsored_fee_0": len(rows) - len(paid), "paid_fees": len(paid),
       "paid_fees_by_others": sum(not r["mine"] for r in paid),
       "formula_exact": sum(r["formula"].startswith("exact") for r in paid), "payout_exact": sum(bool(r["payout"]) for r in paid), "other_payouts": len(other),
       "other_payouts_by_value_rls": dict(vals.most_common()), "rows": rows}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "evidence"), exist_ok=True)
name = f"fresh_check_{TO}{'_selftest' if SELF_TEST else ''}.json"
json.dump(res, open(os.path.join(os.path.dirname(__file__), "..", "evidence", name), "w"), indent=1)
print(f"blocks {FROM:,} to {TO:,} (fresh from the public RPC, no saved files)")
for r in paid: print(f"  {r['time'][:23]}  {'me   ' if r['mine'] else 'other'}  fee {r['fee_rls']:>12} RLS  formula {r['formula']:<32} payout {'yes ' + r['commission_rls'] if r['payout'] else 'MISSING'}")
print(f"fee events: {res['public_fee_events']}  sponsored (fee 0): {res['sponsored_fee_0']}  paid: {res['paid_fees']} ({res['paid_fees_by_others']} by other accounts)")
print(f"paid fees: {res['paid_fees']}   formula exact: {res['formula_exact']}   15/115 payout exact: {res['payout_exact']}")
print(f"other payouts (fees paid privately from shielded RLS): {res['other_payouts']}  {res['other_payouts_by_value_rls']}")

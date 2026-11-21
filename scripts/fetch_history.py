"""Rebuild every Enygma Public forwarder fee on Rayls testnet and match it to the 15% commission payout.
Public RPC + Blockscout API only. Writes evidence/raw/*.json and evidence/fees_history.csv, evidence/payouts.csv,
evidence/token_fees.csv, evidence/history_summary.json.
Run: python fetch_history.py [--to-block N]   (pin --to-block to reproduce a snapshot exactly)"""
import json, os, sys, csv, statistics, collections
from concurrent.futures import ThreadPoolExecutor
from eth_abi import decode
from common import *

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence")
os.makedirs(f"{OUT}/raw", exist_ok=True)
TO = int(sys.argv[sys.argv.index("--to-block") + 1]) if "--to-block" in sys.argv else int(rpc("eth_blockNumber", []), 16)
RLS_PER_GAS = 2_400_000_000_000  # relayer /info rlsPerGas on 20 Nov 2026 (wei RLS per gas unit)
REGISTRY = "0xa473291ffb33e2276f364fae169f03c4406719e9"
VAULTS = {"0x97b5d78dbe06d8c8c843f87b5aa2d8587b890795": "RLS vault", "0x1edb224cf8637f92efadaf47ef9e70c044d75584": "USDr vault",
          "0x9c5ad5e5ea5b5910e7fd1e1cc7b70ce0e4bf06c2": "Shared vault"}
SEL = {"0x8304e41b": "register", "0xc4b3d45c": "shield", "0xb76080b2": "shield", "0x2b460e5f": "shield", "0x94ca3cef": "shield",
       "0x598b8e71": "shield", "0x97bc3503": "shield (NFT)", "0x1d7c55a2": "unshield", "0x3bbc2aec": "unshield", "0x6a0dd2be": "unshield",
       "0xb511a7b3": "unshield", "0xaacd552c": "shielded transfer", "0x72bef65d": "shielded transfer", "0xed59313a": "set username",
       "0xe79a198f": "unregister", "0xd41ad212": "set personal key"}
EXEC_TYPES = ["(address,address,uint256,uint256,uint256,uint256,bytes)", "bytes", "(uint256,uint256,uint8,bytes32,bytes32)"]

def get_logs(addr_):
    out, start = [], 0
    while True:
        r = api(module="logs", action="getLogs", address=addr_, fromBlock=start, toBlock=TO, topic0=RELAYED)["result"]
        out += r
        if len(r) < 1000: break
        start = int(r[-1]["blockNumber"], 16)  # page on; dedupe below
    seen, uniq = set(), []
    for l in out:
        k = (l["transactionHash"], l["logIndex"])
        if k not in seen: seen.add(k); uniq.append(l)
    return uniq

def tokentx(a):
    out, page = [], 1
    while True:
        r = api(module="account", action="tokentx", address=a, startblock=0, endblock=TO, sort="asc", page=page, offset=1000)["result"]
        out += r
        if len(r) < 1000: break
        page += 1
    return out

def detail(h):
    """tx input + gas: public RPC first; old txs the RPC no longer serves come from the Blockscout v2 API."""
    tx = rc = None
    for i in range(3):
        tx = rpc("eth_getTransactionByHash", [h]); rc = rpc("eth_getTransactionReceipt", [h])
        if tx and rc: break
        time.sleep(1 + i)
    if tx and rc:
        d = {"src": "rpc", "gas_used": int(rc["gasUsed"], 16), "gas_price": int(rc.get("effectiveGasPrice") or tx["gasPrice"], 16)}
        inp = tx["input"]
    else:
        for i in range(5):
            try:
                b = requests.get(f"{EXPLORER}/api/v2/transactions/{h}", timeout=60).json(); break
            except Exception: time.sleep(2 + i)
        d = {"src": "blockscout", "gas_used": int(b["gas_used"]), "gas_price": int(b["gas_price"])}
        inp = b["raw_input"]
    tx = {"input": inp}
    d["input_sel"] = inp[:10]
    if inp[:10] == "0x82ad56cb":  # Multicall3 aggregate3: the forwarder execute is one of the calls
        (calls,) = decode(["(address,bool,bytes)[]"], bytes.fromhex(inp[10:]))
        ex = [c[2] for c in calls if c[0].lower() in FORWARDERS and c[2][:4].hex() == "e2076320"]
        d["batched"] = "Multicall3 (" + str(len(calls)) + " calls)"
        if ex: inp = "0x" + ex[0].hex()
    if inp[:10] == "0xe2076320":
        req, sig, permit = decode(EXEC_TYPES, bytes.fromhex(inp[10:]))
        d.update(req_gas=req[2], req_fee=req[5], inner_sel="0x" + req[6][:4].hex(), data_len=len(req[6]), permit_value=permit[0])
    return h, d

def priced(fee):
    q, rem = divmod(fee * 100, 115 * RLS_PER_GAS)
    return q if rem == 0 else round(fee * 100 / 115 / RLS_PER_GAS, 3)

from eth_utils import keccak
_names, _sels = {}, {}
def _t(i): return "(" + ",".join(_t(c) for c in i["components"]) + ")" + i["type"][5:] if i["type"].startswith("tuple") else i["type"]
def contract_info(a):
    """name + function selectors of a verified contract (follows EIP-1967 proxies) from Blockscout"""
    if a in _names: return _names[a]
    j = requests.get(f"{EXPLORER}/api/v2/addresses/{a}", timeout=60).json()
    name = j.get("name") or ("contract" if j.get("is_contract") else "EOA")
    impls = [i.get("address_hash") or i.get("address") for i in (j.get("implementations") or [])]
    sels = {}
    for c in [a] + impls:
        abi = requests.get(f"{EXPLORER}/api/v2/smart-contracts/{c}", timeout=60).json().get("abi") or []
        for f in abi:
            if f.get("type") == "function":
                sels["0x" + keccak(text=f["name"] + "(" + ",".join(_t(i) for i in f["inputs"]) + ")")[:4].hex()] = f["name"]
    _names[a] = (name, sels); return _names[a]

logs = []
for f, name in FORWARDERS.items():
    L = get_logs(f); json.dump(L, open(f"{OUT}/raw/relayed_{f}.json", "w"))
    for l in L: l["_forwarder"] = name
    logs += L
pay = tokentx(COMMISSION); json.dump(pay, open(f"{OUT}/raw/tokentx_commission_address.json", "w"))
hashes = sorted({l["transactionHash"] for l in logs})
CACHE = f"{OUT}/raw/forwarder_tx_details.json"
det = json.load(open(CACHE)) if os.path.exists(CACHE) and "--refresh" not in sys.argv else {}
det = {h: v for h, v in det.items() if v.get("v") == 2}
todo = [h for h in hashes if h not in det]
with ThreadPoolExecutor(8) as ex:
    for h, v in ex.map(detail, todo): v["v"] = 2; det[h] = v
json.dump(det, open(f"{OUT}/raw/forwarder_tx_details.json", "w"))

rows = []
for l in logs:
    d = l["data"][2:]; fee = int(d[64:128], 16); ts = int(l["timeStamp"], 16); h = l["transactionHash"]; x = det[h]
    to = addr(l["topics"][2]).lower()
    action = SEL.get(x.get("inner_sel"))
    tname = "UserRegistry" if to == REGISTRY else VAULTS.get(to)
    if action is None or tname is None:
        cn, sels = contract_info(to); tname = tname or cn
        action = action or (sels.get(x.get("inner_sel"), x.get("inner_sel")) + f" ({cn})")
    y_formula = (x["req_gas"] + 150000 + 16 * (x["data_len"] + 700)) if "req_gas" in x else None
    rows.append({"tx": h, "block": int(l["blockNumber"], 16), "ts": ts, "time_utc": times(ts)[0], "date_utc": times(ts)[0][:10],
                 "forwarder": l["_forwarder"], "account": addr(l["topics"][1]), "target": to,
                 "target_name": tname, "action": action,
                 "fee_rls_wei": fee, "fee_rls": fmt(fee), "expected_commission_wei": fee * 15 // 115,
                 "chain_gas_used": x["gas_used"], "gas_price_wei": x["gas_price"], "relayer_paid_usdr_wei": x["gas_used"] * x["gas_price"],
                 "req_gas": x.get("req_gas"), "calldata_bytes": x.get("data_len"),
                 "priced_gas_units": priced(fee),
                 "formula_gas_units": y_formula, "batched": x.get("batched", ""), "tx_data_source": x["src"]})
rows.sort(key=lambda r: (r["block"], r["tx"]))

# commission payouts: RLS relayer -> commission address
payouts = [p for p in pay if p["from"].lower() == RELAYER and p["tokenSymbol"] == "RLS" and p["to"].lower() == COMMISSION]
for p in payouts: p["_used"] = False
byval = collections.defaultdict(list)
for p in payouts: byval[int(p["value"])].append(p)
for r in rows:
    r["commission_tx"] = ""; r["commission_wei"] = ""; r["commission_delay_s"] = ""; r["ratio_check_15_115"] = "n/a (fee 0)" if r["fee_rls_wei"] == 0 else "no payout found"
    if r["fee_rls_wei"] == 0: continue
    for p in byval.get(r["expected_commission_wei"], []):
        if not p["_used"] and r["block"] <= int(p["blockNumber"]) <= r["block"] + 600:
            p["_used"] = True; r["commission_tx"] = p["hash"]; r["commission_wei"] = int(p["value"])
            r["commission_delay_s"] = int(p["timeStamp"]) - r["ts"]; r["ratio_check_15_115"] = "exact"
            break
# formula check: fee == (formula_gas_units + extra) * rlsPerGas * 115/100 ; extra = 0 or 100000 (token-fee path)
for r in rows:
    if r["fee_rls_wei"] and r["formula_gas_units"]:
        pg = r["priced_gas_units"]; fg = r["formula_gas_units"]
        r["formula_check"] = ("exact" if pg == fg else "exact (+100000 token-fee gas)" if pg == fg + 100000
                              else f"+{pg - fg:.0f} gas (approval-gas term, not reproduced)" if 90000 <= pg - fg <= 100000
                              else f"diff {pg - fg:+.0f} gas")
    else: r["formula_check"] = "n/a"

FIELDS = ["date_utc", "time_utc", "tx", "block", "forwarder", "account", "action", "target_name", "fee_rls", "fee_rls_wei",
          "expected_commission_wei", "commission_wei", "commission_tx", "commission_delay_s", "ratio_check_15_115",
          "chain_gas_used", "gas_price_wei", "relayer_paid_usdr_wei", "req_gas", "calldata_bytes", "priced_gas_units",
          "formula_gas_units", "formula_check", "batched", "tx_data_source"]
with open(f"{OUT}/fees_history.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

# payouts not tied to a forwarder fee: shielded-fee actions (private sends, invites, shielded-paid shields)
un = [p for p in payouts if not p["_used"]]
with open(f"{OUT}/payouts.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["date_utc", "time_utc", "payout_tx", "block", "commission_rls", "commission_wei", "matched_forwarder_fee",
                                    "implied_gas_fee_rls (x115/15)", "implied_gas_units_at_2.4e12"])
    for p in payouts:
        v = int(p["value"]); ts = int(p["timeStamp"])
        w.writerow([times(ts)[0][:10], times(ts)[0], p["hash"], p["blockNumber"], fmt(v), v, "yes" if p["_used"] else "no",
                    fmt(v * 115 // 15), round(v * 115 / 15 / 1.15 / RLS_PER_GAS)])

# 0.25% stablecoin fees: USDr transfers into the commission address from accounts
tok = [p for p in pay if p["tokenSymbol"] == "USDr" and p["to"].lower() == COMMISSION]
with open(f"{OUT}/token_fees.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["date_utc", "tx", "from", "usdr", "usdr_wei", "implied_amount_at_0.25pct (fee/0.0025)"])
    for p in tok:
        v = int(p["value"]); w.writerow([times(int(p["timeStamp"]))[0], p["hash"], p["from"], fmt(v), v, fmt(v * 10000 // 25)])

paid = [r for r in rows if r["fee_rls_wei"]]
summ = {"snapshot_to_block": TO, "snapshot_time_utc": times(int(rpc("eth_getBlockByNumber", [hex(TO), False])["timestamp"], 16))[0],
        "relayed_events": len(rows), "relayed_txs": len({r["tx"] for r in rows}),
        "by_forwarder": collections.Counter(r["forwarder"] for r in rows), "by_action": collections.Counter(r["action"] for r in rows),
        "fee_zero (sponsored)": sum(1 for r in rows if r["fee_rls_wei"] == 0),
        "paid_fees": len(paid), "commission_matched_exact": sum(1 for r in paid if r["ratio_check_15_115"] == "exact"),
        "commission_not_found": sum(1 for r in paid if r["ratio_check_15_115"] != "exact"),
        "formula_check": collections.Counter(r["formula_check"] if not r["formula_check"].startswith("diff") else "differs (earlier pricing version)" for r in paid),
        "median_fee_rls_by_action": {a: fmt(int(statistics.median([r["fee_rls_wei"] for r in paid if r["action"] == a])))
                                     for a in sorted({r["action"] for r in paid})},
        "total_forwarder_fees_rls": fmt(sum(r["fee_rls_wei"] for r in paid)),
        "total_commission_matched_rls": fmt(sum(r["commission_wei"] for r in paid if r["commission_wei"] != "")),
        "commission_payouts_total": len(payouts), "payouts_not_tied_to_forwarder_fee": len(un),
        "payouts_not_tied_total_rls": fmt(sum(int(p["value"]) for p in un)),
        "unmatched_payout_value_counts": collections.Counter(fmt(int(p["value"])) for p in un).most_common(12),
        "usdr_token_fee_transfers_in": len(tok),
        "median_commission_delay_s": statistics.median([r["commission_delay_s"] for r in paid if r["commission_delay_s"] != ""]) if paid else None,
        "first_relayed_utc": rows[0]["time_utc"] if rows else None, "last_relayed_utc": rows[-1]["time_utc"] if rows else None}
# split at the first exact 15/115 payout: before it the testnet ran an earlier fee version with no separate payout
first = min((r for r in paid if r["ratio_check_15_115"] == "exact"), key=lambda r: r["block"])
cur = [r for r in paid if r["block"] >= first["block"]]
summ["current_fee_version"] = {
    "from_utc": first["time_utc"], "from_tx": first["tx"], "paid_fees": len(cur),
    "commission_exact": sum(1 for r in cur if r["ratio_check_15_115"] == "exact"),
    "commission_not_found": [(r["time_utc"], r["tx"]) for r in cur if r["ratio_check_15_115"] != "exact"],
    "formula": collections.Counter(r["formula_check"] if not r["formula_check"].startswith("diff") else "differs" for r in cur),
    "formula_differs_txs": [(r["time_utc"], r["tx"], r["formula_check"]) for r in cur if r["formula_check"].startswith("diff")],
    "fees_rls": fmt(sum(r["fee_rls_wei"] for r in cur)),
    "commission_rls": fmt(sum(r["commission_wei"] for r in cur if r["commission_wei"] != "")),
    "shielded_fee_payouts_after": sum(1 for p in un if int(p["blockNumber"]) >= first["block"]),
    "shielded_fee_payouts_rls": fmt(sum(int(p["value"]) for p in un if int(p["blockNumber"]) >= first["block"])),
    "shielded_payouts_before": sum(1 for p in un if int(p["blockNumber"]) < first["block"]),
}
summ["earlier_version"] = {"paid_fees": len(paid) - len(cur), "until_utc": first["time_utc"]}
json.dump(summ, open(f"{OUT}/history_summary.json", "w"), indent=1, default=str)
print(json.dumps(summ, indent=1, default=str))

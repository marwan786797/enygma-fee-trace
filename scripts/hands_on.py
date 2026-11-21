"""Re-check every step of the hands-on testnet run (throwaway accounts @railfeetrace1 / @railfeetrace2).
For each tx: time (UTC + IST), chain gas the relayer paid (USDr), the RLS fee, the separate 15% payout, and the
fee recomputed from the formula in the wallet's own code. Writes evidence/hands_on_steps.json + .md. Public RPC only."""
import json, os
from eth_abi import decode
from common import *
from trace_tx import trace

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence")
RLS_PER_GAS = 2_400_000_000_000
A = "0x4f1aa6CB2C8932583F2844a855fB057C589F23E9"; B = "0x9d42151e47511d72DbBDD54824053a88F343d3e0"
# quoted = what the relayer quoted to the wallet (saved from the app's network log, evidence/browser_*.log)
STEPS = [
 ("Faucet: 50 test RLS to account A", "0xd2dda180d431c7f354e4cfc7f13611f881ba7fa0701ac17949fb2ae71a0612fd", None, "faucet"),
 ("Faucet: 50 test RLS to account B", "0x958989528701cb4b46cf7f6e212459f24dbba6cac0c8fa010bac1c819bbf4639", None, "faucet"),
 ("A registers @railfeetrace1 (gas from public RLS)", "0x150f72f03097bea38cd561dd7a218f020e75704c3c8461b6827dec93d8a11ae3", 7200072720000000000, "forwarder"),
 ("A shields 20 RLS (gas from public RLS)", "0x7f40bd66f847847a14bcbfa0920a892d22124a23f98147957dc63c5913ed33c5", 3525963480000000000, "forwarder"),
 ("B registers @railfeetrace2 (gas from public RLS)", "0xdf23fa21962a96cba37b0ca8e3853493d0a1fa6032d54b52ade26ec7902bf19e", 7200072720000000000, "forwarder"),
 ("A pays B 5 RLS privately (gas from shielded RLS)", "0xcf03bec70572a7e00f1c7fa0edd578791a3ab32b6ec8f660cde4f21a1bc7760b", 4416000000000000000, "private"),
 ("A unshields 3 RLS to its own address (gas from public RLS)", "0x32ebfef8963c9af737c77597ea79f5fd2ebce62cd35c754e052be0846e06c159", 4528417560000000000, "forwarder"),
 ("B shields 25 RLS (gas from public RLS)", "0x080ede8a21709093e2ab4ec82e4a0f48e164d3156c4f40216b0b9bf78bbb4142", 3525963480000000000, "forwarder"),
 ("B shields 5 RLS (gas from shielded RLS)", "0x669b2b59a64debf80262ba21a01f7f50b3a783e35b4821163388354795271bc3", 7389723360000000000, "shielded-gas"),
 ("A pays B 3 RLS privately (gas from shielded RLS)", "0x404af8ae6776de39a7f2621a9f8d0091b5bdeed4ce916ebfa7bff0ab908defb0", 4416000000000000000, "private"),
 ("B shields 5 RLS (gas from public RLS)", "0xef3173e279adfcda2ee61b270d4f46f8843a9dc092704608f41c32d76b71c5c6", 3525800640000000000, "forwarder"),
 ("Faucet (reopened): 250 shielded test RLS to account B", "0x8a3387e2c07e86b049c4426b36d4ea6f54fb3eeaa76eec26bbb643f2e68b3919", None, "faucet"),
 ("Faucet (reopened): 10 test USDr to account A", "0xc034dd85c1cbc4025cd6adb4e43657269acd857eb7f28f312e1ca1df87418ce4", None, "faucet"),
 ("A shields 4 USDr (gas from public RLS, 0.25% token fee)", "0x732f75d1fc8cccc6fb0fcc2d79632f40d4d13935eb85bfabf66733eafda9e8c6", 3832963800000000000, "forwarder-token"),
 ("0.25% token fee on the 4 USDr shield (relayer pulls it from A)", "0x60db7c585a66aad2e06ece47d09d74f764522f4373e4bbd33b36c601bf41a706", 4000000000000000000, "token-fee"),
 ("A unshields 2 USDr to its own address (gas from public RLS, 0.25% token fee)", "0xfdaa7706b311a027e937003d49d89a041c086bf1bd5256de66da12c87141e202", 4757765280000000000, "forwarder-token"),
 ("0.25% token fee on the 2 USDr unshield (relayer pulls it from A)", "0xc2211c8322f30275dddbc9dc0d3dcdaf56e2c377d7f2147969524de8f736009e", 2000000000000000000, "token-fee"),
 ("B creates a 30 RLS invite link (gas from shielded RLS)", "0x116ead0d6b4dd02fe7e74a8719ffd5bb8e04a26170d616a779379e06363db7d4", 4416000000000000000, "private"),
 ("C (@railfeetrace3) claims the invite (fee taken from the invite)", "0xbb2c67f40360a36dc6f2c3827e1d2ac63725578fea94208ef064739aefaf1a08", 12696000000000000000, "private-claim"),
 ("B pays A 5 RLS privately (gas from shielded RLS; recorded for the video)", "0x39d9f8d70d908ae11fb8e6818e93b8bf052a1fff47afe49b992443d852d4da94", 4416000000000000000, "private"),
]
# for "token-fee" rows the third field is the token amount the 0.25% applies to
EXEC_TYPES = ["(address,address,uint256,uint256,uint256,uint256,bytes)", "bytes", "(uint256,uint256,uint8,bytes32,bytes32)"]

def inner(h):
    inp = rpc("eth_getTransactionByHash", [h])["input"]
    if inp[:10] == "0x82ad56cb":
        (calls,) = decode(["(address,bool,bytes)[]"], bytes.fromhex(inp[10:]))
        ex = [c[2] for c in calls if c[2][:4].hex() == "e2076320"]
        if not ex: return None, len(calls)
        inp = "0x" + ex[0].hex()
    if inp[:10] != "0xe2076320": return None, None
    req, _, _ = decode(EXEC_TYPES, bytes.fromhex(inp[10:]))
    return req, None

TREASURY = "0x71af09966cbed4434cca97c40fa38b8083548b95"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def usdr_to_treasury(h):
    rc = rpc("eth_getTransactionReceipt", [h])
    return [int(l["data"], 16) for l in rc["logs"] if l["address"].lower() == "0x0000000000000000000000000000000000000400"
            and l["topics"][0] == TRANSFER and "0x" + l["topics"][2][-40:] == TREASURY]

rows = []
for label, h, quoted, kind in STEPS:
    t = trace(h, search_blocks=120)
    r = {"step": label, "kind": kind, "tx": h, "link": t["link"], "time_utc": t["time_utc"], "time_ist": t["time_ist"],
         "status": t["status"], "gas_used": t["gas_used"], "gas_price_wei": t["gas_price_wei"],
         "relayer_paid_chain_gas_usdr": fmt(t["chain_gas_paid_usdr_wei"]), "quoted_fee_rls": fmt(quoted) if quoted else None}
    if kind == "faucet":
        r["transfers"] = t["transfers"]; rows.append(r); continue
    if kind == "token-fee":
        r["quoted_fee_rls"] = None
        exp = -(-quoted * 25 // 10000)
        tf = [x for x in usdr_to_treasury(h)]
        r["token_fee_usdr"] = fmt(tf[0]) if tf else None; r["fee_rls_paid"] = (fmt(tf[0]) + " USDr") if tf else None
        r["formula"] = f"ceil({fmt(quoted)} USDr x 25 / 10000) = {fmt(exp)} USDr, sent to 0x71AF"
        r["formula_fee_rls"] = fmt(exp) + " USDr"; r["formula_matches"] = bool(tf) and tf[0] == exp
        r["fee_source"] = "USDr Transfer log to 0x71AF09 in this tx (relayer-sent authorized transfer, selector 0x284854e5, to the USDr precompile)"
        rows.append(r); continue
    fee = t["rls_fee_wei"] if kind.startswith("forwarder") else quoted   # private fees are paid inside the shielded proof: not visible onchain
    r["fee_rls_paid"] = fmt(fee); r["fee_source"] = "Relayed event (onchain)" if kind.startswith("forwarder") else "relayer response + app screen (fee note is shielded)"
    r["quote_equals_paid"] = (fee == quoted)
    share = fee * 15 // 115; r["expected_commission_rls (fee x 15/115)"] = fmt(share)
    m = [p for p in t["payouts_after"] if p["token"] == "RLS" and p["wei"] == share]
    r["commission_tx"] = m[0]["link"] if m else None; r["commission_rls"] = fmt(m[0]["wei"]) if m else None
    r["commission_time_utc"] = m[0]["time_utc"] if m else None; r["commission_time_ist"] = m[0]["time_ist"] if m else None
    r["gas_units_priced"] = fee * 100 / 115 / RLS_PER_GAS
    req, ncalls = inner(h)
    if kind == "forwarder" and req:
        y = req[2] + 150000 + 16 * (len(req[6]) + 700)
        r["formula"] = f"(req.gas {req[2]} + 150000 + 16 x ({len(req[6])} calldata bytes + 700)) = {y} gas x 2.4e12 x 115/100"
        r["formula_fee_rls"] = fmt(y * RLS_PER_GAS * 115 // 100); r["formula_matches"] = (y * RLS_PER_GAS * 115 // 100 == fee)
    elif kind == "forwarder-token" and req:
        y = req[2] + 150000 + 16 * (len(req[6]) + 700) + 100000
        r["formula"] = f"(req.gas {req[2]} + 150000 + 16 x ({len(req[6])} calldata bytes + 700) + 100000 token-fee gas) = {y} gas x 2.4e12 x 115/100"
        r["formula_fee_rls"] = fmt(y * RLS_PER_GAS * 115 // 100); r["formula_matches"] = (y * RLS_PER_GAS * 115 // 100 == fee)
    elif kind == "private-claim":
        r["formula"] = "flat: invite claim 4,600,000 gas x 2.4e12 x 115/100, taken out of the 30 RLS invite (app: 11.04 gas + 1.66 commission)"
        r["formula_fee_rls"] = fmt(4_600_000 * RLS_PER_GAS * 115 // 100); r["formula_matches"] = (4_600_000 * RLS_PER_GAS * 115 // 100 == fee)
    elif kind == "private":
        r["formula"] = "flat: Wr 1,600,000 gas x 2.4e12 x 115/100 (RLS payment, fee note in the same proof)"
        r["formula_fee_rls"] = fmt(1_600_000 * RLS_PER_GAS * 115 // 100); r["formula_matches"] = (1_600_000 * RLS_PER_GAS * 115 // 100 == fee)
    elif kind == "shielded-gas" and req:
        y = req[2] + 150000 + 16 * (len(req[6]) + 700)
        r["formula"] = f"(req.gas {req[2]} + 150000 + 16 x ({len(req[6])} + 700) + Gr 1,400,000) = {y + 1_400_000} gas x 2.4e12 x 115/100"
        r["formula_fee_rls"] = fmt((y + 1_400_000) * RLS_PER_GAS * 115 // 100); r["formula_matches"] = ((y + 1_400_000) * RLS_PER_GAS * 115 // 100 == fee)
    r["rls_transfers_in_tx"] = [x for x in t["transfers"]]
    rows.append(r)

json.dump(rows, open(f"{OUT}/hands_on_steps.json", "w"), indent=1)
with open(f"{OUT}/hands_on_steps.md", "w") as f:
    f.write("| # | Step | Tx | UTC | IST | Fee paid (RLS) | Quote = paid | 15% payout (RLS) | Payout tx | Formula match | Relayer chain gas (USDr) |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for i, r in enumerate(rows, 1):
        f.write(f"| {i} | {r['step']} | [{r['tx'][:10]}…]({r['link']}) | {r['time_utc']} | {r['time_ist']} | {r.get('fee_rls_paid','')} | {r.get('quote_equals_paid','')} | "
                f"{r.get('commission_rls','')} | {('[' + r['commission_tx'].split('/')[-1][:10] + '…](' + r['commission_tx'] + ')') if r.get('commission_tx') else ''} | {r.get('formula_matches','')} | {r['relayer_paid_chain_gas_usdr']} |\n")
for r in rows: print(r["step"], "|", r.get("fee_rls_paid"), r.get("quote_equals_paid"), r.get("commission_rls"), r.get("formula_matches"), r["time_ist"])

"""Trace one Enygma Public tx to the wei: chain gas, RLS fee to relayer, 15% commission payout, 0.25% token fee.
Usage: python trace_tx.py <txhash> [<txhash> ...]  -> prints JSON. Public RPC only."""
import sys, json
from common import *

def trace(h, search_blocks=200):
    tx = rpc("eth_getTransactionByHash", [h]); rc = rpc("eth_getTransactionReceipt", [h])
    blk = rpc("eth_getBlockByNumber", [rc["blockNumber"], False]); ts = int(blk["timestamp"], 16)
    gas_used = int(rc["gasUsed"], 16); gp = int(rc.get("effectiveGasPrice") or tx["gasPrice"], 16)
    out = {"tx": h, "link": txlink(h), "status": int(rc["status"], 16), "block": int(rc["blockNumber"], 16),
           "time_utc": times(ts)[0], "time_ist": times(ts)[1], "from": tx["from"], "to": tx["to"],
           "method_selector": tx["input"][:10], "gas_limit": int(tx["gas"], 16), "gas_used": gas_used,
           "gas_price_wei": gp, "chain_gas_paid_usdr_wei": gas_used * gp, "transfers": [], "relayed": []}
    for lg in rc["logs"]:
        t0 = lg["topics"][0] if lg["topics"] else None
        if t0 == TRANSFER and len(lg["topics"]) == 3:
            tok = lg["address"].lower()
            out["transfers"].append({"token": "RLS" if tok == RLS else ("USDr" if tok == USDR else tok),
                                     "from": addr(lg["topics"][1]), "to": addr(lg["topics"][2]), "wei": int(lg["data"], 16)})
        elif t0 == RELAYED:
            d = lg["data"][2:]
            out["relayed"].append({"forwarder": lg["address"].lower(), "from": addr(lg["topics"][1]), "to": addr(lg["topics"][2]),
                                   "relayer": addr(lg["topics"][3]), "nonce": int(d[:64], 16), "fee_wei": int(d[64:128], 16)})
    # gas fee charged in RLS: Relayed.fee (forwarder path)
    fee = sum(r["fee_wei"] for r in out["relayed"])
    out["rls_fee_wei"] = fee
    out["expected_share_wei"] = fee * 15 // 115  # wallet bundle: zr(e) = e*15n/115n
    # find the separate payout tx(s) relayer -> commission address after this block
    start = out["block"]; end = start + search_blocks
    lst = api(module="account", action="tokentx", address=COMMISSION, startblock=start, endblock=end, sort="asc")["result"]
    out["payouts_after"] = [{"tx": x["hash"], "link": txlink(x["hash"]), "block": int(x["blockNumber"]), "token": x["tokenSymbol"],
                             "from": x["from"], "wei": int(x["value"]), "time_utc": times(int(x["timeStamp"]))[0],
                             "time_ist": times(int(x["timeStamp"]))[1]}
                            for x in lst if x["from"].lower() == RELAYER and x["hash"].lower() != h.lower()]
    m = [p for p in out["payouts_after"] if p["token"] == "RLS" and p["wei"] == out["expected_share_wei"] and fee > 0]
    out["share_match"] = m[0] if m else None
    if fee:  # fee = gas_units * rlsPerGas * 115/100  ->  gas units the fee was priced on
        out["fee_gas_units_at_2.4e12"] = fee * 100 / 115 / 2_400_000_000_000
    return out

if __name__ == "__main__":
    print(json.dumps([trace(h) for h in sys.argv[1:]], indent=1))

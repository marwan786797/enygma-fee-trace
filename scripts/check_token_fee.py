"""Check the 0.25% stablecoin fee: every USDr transfer from an account to the commission address is matched to that
account's USDr shield (account -> vault) or unshield (vault -> account) nearby, and compared to ceil(amount x 25 / 10000)
(the rounding in the wallet code: Rr(e) = (e*25n + 9999n)/10000n). Writes evidence/token_fee_check.csv"""
import csv, os, json, collections
from common import *
import requests
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence")
pay = json.load(open(f"{OUT}/raw/tokentx_commission_address.json"))
fees = [p for p in pay if int(p["timeStamp"]) >= 1793103829 and p["tokenSymbol"] == "USDr" and p["to"].lower() == COMMISSION and p["from"].lower() != RELAYER]
VAULTS = ["0x1edb224cf8637f92efadaf47ef9e70c044d75584", "0x9c5ad5e5ea5b5910e7fd1e1cc7b70ce0e4bf06c2"]
moves = []
for v in VAULTS:
    page = 1
    while True:
        r = api(module="account", action="tokentx", address=v, contractaddress=USDR, sort="asc", page=page, offset=1000)["result"]
        moves += [dict(x, _vault=v) for x in r]
        if len(r) < 1000: break
        page += 1
json.dump(moves, open(f"{OUT}/raw/usdr_vault_transfers.json", "w"))
used = set(); rows = []
for f in fees:
    u = f["from"].lower(); b = int(f["blockNumber"]); fee = int(f["value"])
    cands = []
    for m in moves:
        if m["hash"] in used: continue
        mb = int(m["blockNumber"])
        if abs(mb - b) > 200: continue
        if m["from"].lower() == u and m["to"].lower() == m["_vault"]: kind = "shield"
        elif m["to"].lower() == u and m["from"].lower() == m["_vault"]: kind = "unshield"
        else: continue
        amt = int(m["value"])
        if (amt * 25 + 9999) // 10000 == fee: cands.append((abs(mb - b), kind, m, amt))
    cands.sort(key=lambda c: c[0])
    if not cands:  # fall back: any USDr move of this account near the fee (shield into another vault/contract, or a public send)
        for m in api(module="account", action="tokentx", address=u, contractaddress=USDR, startblock=b - 200, endblock=b + 200, sort="asc")["result"]:
            if m["hash"] in used or m["hash"] == f["hash"]: continue
            amt = int(m["value"])
            if (amt * 25 + 9999) // 10000 == fee:
                other = m["to"] if m["from"].lower() == u else m["from"]
                info = requests.get(f"{EXPLORER}/api/v2/addresses/{other}", timeout=60).json()
                nm = info.get("name") or ("contract" if info.get("is_contract") else "EOA")
                kind = ("to " if m["from"].lower() == u else "from ") + nm
                cands.append((abs(int(m["blockNumber"]) - b), kind, m, amt))
    cands.sort(key=lambda c: c[0])
    if cands:
        _, kind, m, amt = cands[0]; used.add(m["hash"])
        rows.append([times(int(f["timeStamp"]))[0], f["hash"], u, fmt(fee), kind, m["hash"], fmt(amt), "exact ceil(amount x 0.25%)"])
    else:
        rows.append([times(int(f["timeStamp"]))[0], f["hash"], u, fmt(fee), "", "", "", "no matching shield/unshield found"])
with open(f"{OUT}/token_fee_check.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["time_utc", "fee_tx", "account", "fee_usdr", "action", "action_tx", "amount_usdr", "check"]); w.writerows(rows)
c = collections.Counter(r[-1] for r in rows); print(len(rows), dict(c)); print(collections.Counter(r[4] for r in rows))
json.dump({"usdr_fee_transfers": len(rows), "result": dict(c)}, open(f"{OUT}/token_fee_summary.json", "w"), indent=1)

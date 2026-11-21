"""Charts from evidence/fees_history.csv + payouts.csv -> charts/*.png"""
import csv, os, collections, statistics
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = list(csv.DictReader(open(f"{BASE}/evidence/fees_history.csv")))
P = list(csv.DictReader(open(f"{BASE}/evidence/payouts.csv")))
paid = [r for r in R if int(r["fee_rls_wei"]) > 0]
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})

# 1. per day: paid gas fees whose 15% payout matched to the wei, vs no payout found
days = sorted({r["date_utc"] for r in paid})
ok = collections.Counter(r["date_utc"] for r in paid if r["ratio_check_15_115"] == "exact")
no = collections.Counter(r["date_utc"] for r in paid if r["ratio_check_15_115"] != "exact")
sh = collections.Counter(p["date_utc"] for p in P if p["matched_forwarder_fee"] == "no")
alld = sorted(set(days) | set(sh))
fig, ax = plt.subplots(figsize=(12, 5.5))
x = range(len(alld))
ax.bar(x, [ok[d] for d in alld], color="#7b61ff", label="Public RLS gas fee whose 15% payout matches fee x 15/115 to the wei")
ax.bar(x, [sh[d] for d in alld], bottom=[ok[d] for d in alld], color="#2bb673", label="15% payout with no public fee tx (fee paid privately, from shielded RLS)")
ax.bar(x, [no[d] for d in alld], bottom=[ok[d] + sh[d] for d in alld], color="#c9c9d4", label="Public RLS gas fee with no 15% payout found (almost all before 9 Nov, earlier fee version)")
ax.set_xticks(list(x)); ax.set_xticklabels([d[5:] for d in alld], rotation=60, fontsize=9)
ax.set_ylabel("transactions per day"); ax.set_title("Enygma Public testnet: gas fees and their separate 15% commission payout, per day (UTC)")
ax.legend(frameon=False, fontsize=10, loc="upper left"); fig.text(0.01, 0.01, "Source: Rayls testnet explorer API + public RPC, rebuilt by scripts/fetch_history.py", fontsize=8, color="#666")
fig.tight_layout(); fig.savefig(f"{BASE}/charts/daily_fee_and_commission.png", dpi=150); plt.close(fig)

# 2. median fee per action (RLS), actions with >= 5 paid txs
acts = collections.defaultdict(list)
first = min(int(r["block"]) for r in paid if r["ratio_check_15_115"] == "exact")
CORE = {"register": "register (one time)", "shield": "shield", "unshield": "unshield", "shielded transfer": "shielded transfer via forwarder",
        "sendWithPermit (PublicSender)": "public send, RLS", "sendWithUsdrAuthorization (PublicSender)": "public send, USDr"}
for r in paid:
    if int(r["block"]) >= first and r["action"] in CORE: acts[CORE[r["action"]]].append(int(r["fee_rls_wei"]) / 1e18)
acts["private payment, RLS (flat, from shielded RLS)"] = [4.416]
acts["invite, or private payment in USDr (flat)"] = [8.28]
items = sorted([(a, statistics.median(v), len(v)) for a, v in acts.items()], key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.barh([f"{a} (n={n})" if n > 1 else f"{a} (app quote)" for a, _, n in items], [m for _, m, _ in items], color="#7b61ff")
for i, (_, m, _) in enumerate(items): ax.text(m + 0.05, i, f"{m:.2f} RLS", va="center", fontsize=10)
ax.set_xlabel("median gas fee in test RLS (15% commission included)")
ax.set_title("Median RLS gas fee per Enygma Public action (testnet, since 9 Nov)")
fig.text(0.01, 0.01, "Testnet RLS has no value. Fees = priced gas x 0.0000024 RLS x 115%. Source: scripts/fetch_history.py", fontsize=8, color="#666")
fig.tight_layout(); fig.savefig(f"{BASE}/charts/median_fee_by_action.png", dpi=150); plt.close(fig)

# 3. hands-on breakdown: where one fee goes
import json
H = [h for h in json.load(open(f"{BASE}/evidence/hands_on_steps.json")) if h.get("fee_rls_paid") and h["kind"] != "token-fee"]
fig, ax = plt.subplots(figsize=(12, 8.5))
labels = [h["step"].replace(" (gas from ", "\n(gas from ") for h in H]
fee = [float(h["fee_rls_paid"]) for h in H]; com = [float(h["commission_rls"]) for h in H]
ax.barh(labels, [f - c for f, c in zip(fee, com)], color="#b9a8ff", label="relayer part (100 parts; it also pays the chain gas in USDr)")
ax.barh(labels, com, left=[f - c for f, c in zip(fee, com)], color="#7b61ff", label="15% commission, paid on to 0x71AF...8B95 in a separate tx (15 parts)")
from decimal import Decimal as D
for i, h in enumerate(H): ax.text(fee[i] + 0.05, i, f"{h['fee_rls_paid']} = {(D(h["fee_rls_paid"]) - D(h["commission_rls"])).normalize():f} + {h['commission_rls']}", va="center", fontsize=9)
ax.set_xlabel("test RLS"); ax.set_title(f"My {len(H)} testnet fee steps, 20 Nov 2026: fee = 100 parts + 15% commission")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1); ax.set_xlim(0, max(fee) * 1.35); ax.invert_yaxis(); ax.tick_params(axis="y", labelsize=9)
fig.tight_layout(); fig.savefig(f"{BASE}/charts/hands_on_fee_split.png", dpi=150); plt.close(fig)
print("charts written")

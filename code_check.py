"""Pull the live Enygma wallet bundle and print the fee constants + formulas it ships (the relayer module inside it).
Saves a copy + sha256 to evidence/wallet_bundle/. Public web only."""
import re, hashlib, os, requests, json
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence", "wallet_bundle")
os.makedirs(OUT, exist_ok=True)
html = requests.get("https://enygma-testnet.rayls.com/", timeout=60).text
name = re.search(r"assets/(index-[A-Za-z0-9_-]+\.js)", html).group(1)
url = f"https://enygma-testnet.rayls.com/assets/{name}"
js = requests.get(url, timeout=120).text
open(f"{OUT}/{name}", "w").write(js)
sha = hashlib.sha256(js.encode()).hexdigest()
pats = {
 "constants (commission address, token fee bps, gas share %, extra gas terms)": r"var \w+=`0x71AF[0-9a-fA-F]+`,\w+=\d+n,\w+=\d+n,\w+=\d+n,\w+=\d+n,\w+=\d+,\w+=\d+n,\w+=\d+n,\w+=`[0-9.]+`",
 "gas padding Ir(e)": r"function \w+\(e\)\{return e\*12n/10n\+20000n\}",
 "priced gas Lr(e,t,n)": r"function \w+\(e,t,n=!1\)\{let r=e\+\w+\+\w+\*BigInt\(t\+\w+\);return n\?r\+\w+:r\}",
 "token fee ceil(amount*25/10000)": r"function \w+\(e\)\{return\(e\*\w+\+9999n\)/10000n\}",
 "commission share fee*15/115": r"function \w+\(e\)\{return e\*\w+/115n\}",
 "gas fee = gas * rlsPerGas * 115/100": r"function \w+\(e,t\)\{return e\*t\*115n/100n\}",
 "shielded payment gas constants": r"\w+=50n,\w+=1600000n,\w+=1400000n",
}
res = {"bundle_url": url, "sha256": sha, "found": {}}
for k, p in pats.items():
    m = re.search(p, js); res["found"][k] = m.group(0) if m else None
json.dump(res, open(f"{OUT}/formula_snippets.json", "w"), indent=1)
print(json.dumps(res, indent=1))

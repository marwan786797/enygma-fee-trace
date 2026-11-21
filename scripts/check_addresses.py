"""Label every address used in the write-up by type, from the testnet explorer API (not from guesses).
EOA = no contract code (a normal key-held wallet). Contract types come from Blockscout's verified name / proxy type.
Writes evidence/address_types.json + .md"""
import json, os, requests
from common import EXPLORER, rpc
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence")
ADDR = {
 "0xa5f0C684EB49866a9f62f901Cd85f98a19DA0Ac8": "Relayer (relayer /info 'relayer'; sender of every relayed tx)",
 "0x71AF09966CBED4434ccA97c40Fa38B8083548B95": "Receives the 15% commission and 0.25% token fee (relayer /info 'treasury'; app config also lists it as auditor)",
 "0x12B6640048DEB2e8fFDa4Bc10Bb2a640B70eCA6d": "Gas forwarder, current (relayer /info 'forwarder')",
 "0x753cc3Abe9A1c49536ee74F1f424fCF693AAB5DD": "Gas forwarder, earlier",
 "0xA473291FFb33e2276F364fAE169f03c4406719e9": "User registry",
 "0x9C5Ad5e5Ea5b5910E7fD1E1CC7b70ce0e4bF06c2": "Shared vault",
 "0x97b5d78dbe06d8c8c843f87b5aa2d8587b890795": "RLS vault",
 "0x1edb224cf8637f92efadaf47ef9e70c044d75584": "USDr vault",
 "0xBf099175a241194C38E977735D59CCb22596d775": "Owner multisig (docs: upgrades registry + shared vault)",
 "0x07e17E17e17E17e17e17e17E17E17E17E17e17EA": "RLS token on testnet (relayer /info 'rls')",
 "0x0000000000000000000000000000000000000400": "USDr (gas token, precompile)",
 "0x4f1aa6CB2C8932583F2844a855fB057C589F23E9": "Test account A @railfeetrace1 (throwaway key made on the box)",
 "0x9d42151e47511d72DbBDD54824053a88F343d3e0": "Test account B @railfeetrace2 (throwaway key made on the box)",
 "0xD0a85b7571000c6F8dC89699BBCD69862F343C7d": "Test account C @railfeetrace3 (throwaway key made on the box, joined by B's invite)",
 "0x74a6792ddb096873df810edb01ab7e60d2f04524": "Pass-through hop in the USDr shield tx (USDr A -> this -> shared vault); role not documented",
}
rows = []
for a, role in ADDR.items():
    j = requests.get(f"{EXPLORER}/api/v2/addresses/{a}", timeout=60).json()
    code = rpc("eth_getCode", [a, "latest"])
    impl = [i.get("address_hash") or i.get("address") for i in (j.get("implementations") or [])]
    impl_names = [i.get("name") for i in (j.get("implementations") or [])]
    if not j.get("is_contract") and code in ("0x", "0x0"):
        typ = "EOA (normal wallet, no code)"
    elif code in ("0x", "0x0", "0x00"):
        typ = f"precompile (eth_getCode = {code}, no real bytecode); explorer lists it as ERC-20 '{j.get('name')}'"
    else:
        n = j.get("name") or "unverified contract"
        if "Safe" in n or "GnosisSafe" in n: typ = f"Safe contract ({n})"
        elif j.get("proxy_type"): typ = f"{j['proxy_type']} proxy '{n}' -> {impl_names[0] if impl_names else '?'} {impl[0] if impl else ''}"
        else: typ = f"contract '{n}'" + (" (custom multisig, not a Safe)" if "Multisig" in n else "")
    extra = {}
    if "Multisig" in (j.get("name") or ""):
        extra["threshold"] = int(rpc("eth_call", [{"to": a, "data": "0x42cde4e8"}, "latest"]), 16)  # threshold()
    rows.append({"address": a, "type": typ, "role_and_source": role, "verified": j.get("is_verified"),
                 "explorer": f"{EXPLORER}/address/{a}", "api": f"{EXPLORER}/api/v2/addresses/{a}", **extra})
json.dump(rows, open(f"{OUT}/address_types.json", "w"), indent=1)
with open(f"{OUT}/address_types.md", "w") as f:
    f.write("| Address | Type (explorer API) | Role (source) |\n|---|---|---|\n")
    for r in rows: f.write(f"| [{r['address']}]({r['explorer']}) | {r['type']}{' threshold ' + str(r['threshold']) if 'threshold' in r else ''} | {r['role_and_source']} |\n")
for r in rows: print(r["address"], "|", r["type"], r.get("threshold", ""))

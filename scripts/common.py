"""Shared helpers. Public endpoints only: Rayls testnet RPC + Blockscout API. No keys needed."""
import json, time, datetime, requests
RPC = "https://testnet-rpc.rayls.com"
API = "https://testnet-explorer.rayls.com/api"
EXPLORER = "https://testnet-explorer.rayls.com"
RELAYER = "0xa5f0C684EB49866a9f62f901Cd85f98a19DA0Ac8".lower()
COMMISSION = "0x71AF09966CBED4434ccA97c40Fa38B8083548B95".lower()
RLS = "0x07e17E17e17E17e17e17e17E17E17E17E17e17EA".lower()
USDR = "0x0000000000000000000000000000000000000400"
FORWARDERS = {"0x12b6640048deb2e8ffda4bc10bb2a640b70eca6d": "RlsGasForwarder (current)",
              "0x753cc3abe9a1c49536ee74f1f424fcf693aab5dd": "RlsGasForwarder (earlier)"}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
RELAYED = "0x0684ec99c5a024d68812ca8b1a1fc50eb479a6b72828732541183a0a28be4a41"  # keccak Relayed(address,address,uint256,address,uint256)
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def rpc(method, params, tries=5):
    for i in range(tries):
        try:
            r = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=60).json()
            if "error" in r: raise Exception(r["error"])
            return r["result"]
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 * (i + 1))

def api(**q):
    for i in range(5):
        try:
            return requests.get(API, params=q, timeout=120).json()
        except Exception:
            time.sleep(3 * (i + 1))
    raise Exception("api failed")

def addr(topic): return "0x" + topic[-40:]
def fmt(wei, d=18):
    """exact decimal string of an integer wei amount (no float rounding)"""
    wei = int(wei); neg = wei < 0; wei = abs(wei)
    s = f"{wei // 10**d}.{wei % 10**d:0{d}d}".rstrip("0").rstrip(".")
    return ("-" if neg else "") + s
def times(ts):
    u = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    return u.strftime("%Y-%m-%d %H:%M:%S UTC"), u.astimezone(IST).strftime("%Y-%m-%d %I:%M:%S %p IST")
def txlink(h): return f"{EXPLORER}/tx/{h}"

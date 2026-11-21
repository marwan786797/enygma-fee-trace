"""Drives enygma-testnet.rayls.com in headless Chrome with a THROWAWAY testnet key.
The page gets an injected EIP-1193 wallet whose signing happens in Python with the key
file in ../.keys/<NAME>.key (never printed). Commands are read from a FIFO so a human
(or agent) can drive it step by step and take screenshots.
Usage: python browser_driver.py A   (then write JSON lines into /tmp/drv_A.fifo)"""
import json, os, sys, time, requests, traceback
from eth_account import Account
from eth_account.messages import encode_defunct
from playwright.sync_api import sync_playwright

NAME = sys.argv[1]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = open(f"{BASE}/.keys/{NAME}.key").read().strip()
ACCT = Account.from_key(KEY)
RPC = "https://testnet-rpc.rayls.com"
CHAIN = 7295799
FIFO = f"/tmp/drv_{NAME}.fifo"
LOG = open(f"{BASE}/evidence/browser_{NAME}.log", "a")
SIGLOG = open(f"{BASE}/evidence/wallet_requests_{NAME}.jsonl", "a")

def log(*a):
    s = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()

def rpc(method, params):
    r = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=60).json()
    if "error" in r: raise Exception(json.dumps(r["error"]))
    return r["result"]

def wallet(method, params):
    params = params or []
    rec = {"t": time.time(), "method": method}
    try:
        if method in ("eth_requestAccounts", "eth_accounts"): res = [ACCT.address]
        elif method == "eth_chainId": res = hex(CHAIN)
        elif method == "net_version": res = str(CHAIN)
        elif method in ("wallet_switchEthereumChain", "wallet_addEthereumChain", "wallet_watchAsset"): res = None
        elif method == "wallet_requestPermissions": res = [{"parentCapability": "eth_accounts"}]
        elif method == "wallet_getPermissions": res = [{"parentCapability": "eth_accounts"}]
        elif method == "personal_sign":
            msg = params[0]
            m = encode_defunct(hexstr=msg) if msg.startswith("0x") else encode_defunct(text=msg)
            res = "0x" + ACCT.sign_message(m).signature.hex().removeprefix("0x")
            rec["message"] = msg[:400]
        elif method in ("eth_signTypedData_v4", "eth_signTypedData"):
            data = params[1] if isinstance(params[1], (dict, str)) else params[0]
            data = json.loads(data) if isinstance(data, str) else data
            fields = [f["name"] for f in data.get("types", {}).get("EIP712Domain", [])]
            if fields: data["domain"] = {k: v for k, v in data["domain"].items() if k in fields}
            else: data["domain"] = {k: v for k, v in data["domain"].items() if v is not None}
            res = "0x" + Account.sign_typed_data(KEY, full_message=data).signature.hex().removeprefix("0x")
            rec["typed"] = {"primaryType": data.get("primaryType"), "domain": data.get("domain"), "message": data.get("message")}
        elif method == "eth_sendTransaction":
            tx = params[0]
            t = {"to": tx.get("to"), "data": tx.get("data", "0x"), "value": int(tx.get("value", "0x0"), 16),
                 "chainId": CHAIN, "nonce": int(rpc("eth_getTransactionCount", [ACCT.address, "pending"]), 16),
                 "gasPrice": int(rpc("eth_gasPrice", []), 16)}
            t["gas"] = int(tx["gas"], 16) if tx.get("gas") else int(rpc("eth_estimateGas", [{"from": ACCT.address, "to": t["to"], "data": t["data"], "value": hex(t["value"])}]), 16)
            raw = Account.sign_transaction(t, KEY).raw_transaction.hex()
            res = rpc("eth_sendRawTransaction", ["0x" + raw.removeprefix("0x")])
            rec["tx"] = {"to": t["to"], "value": t["value"], "hash": res}
        else:
            res = rpc(method, params)
        rec["ok"] = True
        if method not in ("eth_chainId", "eth_accounts", "eth_blockNumber", "eth_call", "eth_getBalance"):
            SIGLOG.write(json.dumps(rec, default=str) + "\n"); SIGLOG.flush()
        return {"result": res}
    except Exception as e:
        rec["error"] = str(e); SIGLOG.write(json.dumps(rec, default=str) + "\n"); SIGLOG.flush()
        return {"error": {"code": 4001 if "reject" in str(e) else -32603, "message": str(e)}}

SHIM = """
(() => {
  const listeners = {};
  const provider = {
    isMetaMask: false, isBoxTestWallet: true,
    async request({method, params}) {
      const r = await window.__boxWallet(method, params || []);
      if (r.error) { const e = new Error(r.error.message); e.code = r.error.code; throw e; }
      if (method === 'eth_requestAccounts') (listeners['connect']||[]).forEach(f=>f({chainId: '0x%x'}));
      return r.result;
    },
    on(ev, f) { (listeners[ev] = listeners[ev] || []).push(f); return provider; },
    removeListener(ev, f) { listeners[ev] = (listeners[ev]||[]).filter(x=>x!==f); return provider; },
    enable() { return provider.request({method:'eth_requestAccounts'}); },
  };
  window.ethereum = provider;
  const info = {uuid: '6f1c1f3e-1111-4c1a-9a35-0b0b0b0b0b0b', name: 'Box Test Wallet', icon: 'data:image/svg+xml,<svg xmlns=%%22http://www.w3.org/2000/svg%%22/>', rdns: 'box.test.wallet'};
  const announce = () => window.dispatchEvent(new CustomEvent('eip6963:announceProvider', {detail: Object.freeze({info, provider})}));
  window.addEventListener('eip6963:requestProvider', announce); announce();
})();
""" % CHAIN

if not os.path.exists(FIFO): os.mkfifo(FIFO)
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(f"{BASE}/.browser_{NAME}", channel="chrome", headless=True,
                                               viewport={"width": 1280, "height": int(os.environ.get("VH", "1000"))},
                                               device_scale_factor=float(os.environ.get("DPR", "1")),
                                               **({"record_video_dir": os.environ["VIDDIR"], "record_video_size": {"width": 1280, "height": int(os.environ.get("VH", "1000"))}} if os.environ.get("VIDDIR") else {}))
    b = ctx
    ctx.expose_function("__boxWallet", wallet)
    ctx.add_init_script(SHIM)
    page = ctx.new_page()
    page.on("console", lambda m: LOG.write(f"console.{m.type}: {m.text[:500]}\n"))
    def onresp(r):
        if r.status >= 400:
            LOG.write(f"HTTPERR {r.status} {r.request.method} {r.url[:300]} req={(r.request.post_data or '')[:300]}\n"); LOG.flush()
        if "enygma-relayer" in r.url:
            try: body = r.text()[:3000]
            except Exception: body = "?"
            LOG.write(f"RELAYER {r.request.method} {r.url} {r.status} req={(r.request.post_data or '')[:3000]} resp={body}\n"); LOG.flush()
    page.on("response", onresp)
    log("driver up for", NAME, ACCT.address)
    fd = os.open(FIFO, os.O_RDONLY | os.O_NONBLOCK); buf = ""
    while True:
        try: chunk = os.read(fd, 65536).decode()
        except BlockingIOError: chunk = ""
        if not chunk:
            page.wait_for_timeout(300)  # pumps wallet callbacks while idle
            continue
        buf += chunk
        while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line: continue
                try:
                    c = json.loads(line); op = c["op"]
                    if op == "goto": page.goto(c["url"], wait_until="networkidle", timeout=90000)
                    elif op == "gotofile": page.goto(open(c["file"]).read().strip(), wait_until="networkidle", timeout=90000)  # secret links (invite) stay out of logs
                    elif op == "click": page.get_by_text(c["text"], exact=c.get("exact", False)).nth(c.get("n", 0)).click(timeout=c.get("timeout", 20000))
                    elif op == "role": page.get_by_role(c["role"], name=c["name"], exact=c.get("exact", False)).nth(c.get("n", 0)).click(timeout=c.get("timeout", 20000))
                    elif op == "css": page.locator(c["sel"]).nth(c.get("n", 0)).click(timeout=c.get("timeout", 20000))
                    elif op == "fill": page.locator(c["sel"]).nth(c.get("n", 0)).fill(c["value"])
                    elif op == "press": page.keyboard.press(c["key"])
                    elif op == "wait": page.wait_for_timeout(c.get("ms", 2000))
                    elif op == "waittext": page.get_by_text(c["text"]).first.wait_for(timeout=c.get("timeout", 120000))
                    elif op == "shot": page.screenshot(path=c["path"], full_page=c.get("full", False))
                    elif op == "text":
                        open(c.get("path", f"/tmp/drv_{NAME}_text.txt"), "w").write(page.inner_text("body"))
                    elif op == "eval": log("EVAL", json.dumps(page.evaluate(c["js"]), default=str)[:3000])
                    elif op == "quit": b.close(); sys.exit(0)
                    log("OK", line[:200], "url=", page.url.split("#")[0])
                except Exception as e:
                    log("ERR", line[:200], repr(e)[:800])

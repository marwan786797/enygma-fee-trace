# What does a private payment on a public blockchain actually cost?

Rerunnable proof for my Rayls Enygma Public fee trace (testnet pilot, 20 Nov 2026).

**Result:** on the Enygma Public testnet pilot a private payment costs a flat 4.416 test RLS: 3.84 gas plus 0.576 commission (100 parts to 15). I matched the 15 parts onchain to the wei for all 14 fee steps of my own run, for 375 of 378 public fees since 9 Nov 2026, and for 16 of 16 paid fees made after I wrote the formula down (14 of them by other accounts).

Enygma Public is an experimental testnet pilot. Pricing, the rate, the 15% and the test addresses will likely change before mainnet (Alex, Rayls team, r/Rayls, 20 Nov 2026: https://www.reddit.com/r/Rayls/s/EtnvbYGAQ9). Test RLS and USDr have no value. No USD figures are claimed.

## Reproduce in 3 commands

Public data only. No wallet, no keys, no login. Python 3.10+.

```bash
git clone [repo-link] && cd enygma-fee-trace
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fresh_check.py
```

`fresh_check.py` reads nothing saved. It takes every fee after block 24,667,602 from the public RPC and checks it against the formula and its 15/115 payout. Add `--self-test` for the negative control (price and payout moved by 1 wei, every check must fail). Add `--to-block 24692010` to get exactly the window in the article.

Everything else:

```bash
PY=$PWD/.venv/bin/python bash scripts/run_all.sh              # history pinned to block 24667602
REFRESH=1 TO_BLOCK=latest PY=$PWD/.venv/bin/python bash scripts/run_all.sh   # refetch everything, newest block
```

## Fresh from the chain vs saved data

| Check | Reads | Notes |
|---|---|---|
| `fresh_check.py` | public RPC only | out of sample check, about 10 s |
| `hands_on.py` | public RPC only | my 20 steps; app quotes are written into the script from my saved wallet logs |
| `trace_tx.py <hash>` | public RPC | any single Enygma tx |
| `code_check.py` | live wallet bundle | fee constants and functions |
| `check_addresses.py` | explorer API + `eth_getCode` | EOA, contract, proxy, multisig |
| `check_fee_split.sh [block]` | mainnet RPC (foundry `cast`) | FeeAggregator getConfig() |
| `fetch_history.py` | public RPC + Blockscout API, **tx details cached** in `evidence/raw/` | `--refresh` refetches all (about 10 min) |
| `check_token_fee.py` | payout list saved by `fetch_history.py` + Blockscout | 0.25% USDr fees |
| `make_charts.py` | the CSVs | charts only |

Saved and not re-creatable: the app quotes (`evidence/browser_*.log`, `evidence/screens/`). Public fees are checked against the onchain fee; shielded fees against the public payout (payout x 115/15 = fee).

Loaded, not proven: rlsPerGas 0.0000024 RLS (relayer `/info`, confirmed as a fixed test price by the team) and who controls 0x71AF…8B95 (team statement).

## Files

- `findings.md`: every result with its source label (documented, independently verified, my analysis, team confirmed, still unconfirmed).
- `discord-ticket.md`: questions for the Rayls team and their answers.
- `evidence/`: raw chain data, CSVs, fresh check output, wallet bundles, screenshots, app logs.
- `charts/`, `graphics/`: figures used in the article.
- `scripts/browser_driver.py`, `scripts/drv.sh`: how the hands on run was done (headless Chrome, injected wallet signing with a throwaway key that is not in this repo). Needs `requirements-browser.txt`.

### Data dictionary, `evidence/fees_history.csv` (one row per `Relayed` event)

| Column | Meaning | Proven how |
|---|---|---|
| date_utc, time_utc, block, tx | when and where | onchain |
| forwarder | which RlsGasForwarder emitted the event | onchain |
| account | who signed the request (`Relayed.from`) | onchain |
| action, target_name | decoded from the inner call and the target's verified ABI | onchain input + explorer ABI |
| fee_rls, fee_rls_wei | RLS the account paid the relayer (`Relayed.fee`) | onchain |
| expected_commission_wei | floor(fee x 15 / 115) | calculation |
| commission_wei, commission_tx, commission_delay_s | the relayer to 0x71AF transfer with that value within 600 blocks | onchain + calculation |
| ratio_check_15_115 | `exact` if that payout exists | calculation |
| chain_gas_used, gas_price_wei, relayer_paid_usdr_wei | real chain gas the relayer paid in USDr | onchain receipt |
| req_gas, calldata_bytes | from the signed request in the tx input | onchain input |
| priced_gas_units | fee / (rlsPerGas x 1.15) | calculation, rlsPerGas loaded from the relayer API |
| formula_gas_units, formula_check | req_gas + 150000 + 16 x (calldata + 700), and whether it equals priced_gas_units | calculation with the wallet's formula |
| batched | the tx was a Multicall3 batch | onchain input |
| tx_data_source | `rpc` or `blockscout` | n/a |

## Not tested

Mainnet Enygma fees. The relayer's own server code (only its outputs, which match the wallet's relayer module in everything I tested).

The wallet bundles themselves are Rayls' code and are not copied here. `code_check.py` downloads the live one and saves the fee snippets plus its sha256 to `evidence/wallet_bundle/formula_snippets.json`. Checked builds: index-Nw3AggQS.js (used by my run), index-DlzVF1v6.js (sha256 ced27fe6df814a0b897c4c328193f4e8ec9aa3c82ad8f30492cb283012a1989f), index-BRJsQdqQ.js (sha256 05b6ebb65b9114ff75558b007eb42cd92924fe2daf23164e4f8e93245d8044f3), index-Dlv-HYaZ.js (sha256 7530bbc2d7a301c50e28923529cb9315f88145a9a25a7c71db8a1f34afd9ca68, live at 20 Nov 2026 about 10:50 PM IST).

#!/usr/bin/env bash
# Rerun every check in this pack from public data only (no wallet, no keys, no login).
# Usage: bash scripts/run_all.sh                 -> history pinned to block 24667602 (20 Nov 2026 09:41:12 UTC)
#        TO_BLOCK=latest bash scripts/run_all.sh -> history up to the newest block
#        REFRESH=1 bash scripts/run_all.sh       -> also refetch every saved tx detail from the chain (about 10 min)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
$PY -c "import requests, eth_abi, eth_utils, matplotlib" 2>/dev/null || { echo "pip install -r requirements.txt"; exit 1; }
TO=${TO_BLOCK:-24667602}
R=""; [ "${REFRESH:-0}" = 1 ] && R="--refresh"
echo "== 1/7 [fresh] fee formulas in the live Enygma wallet bundle";               $PY code_check.py
echo "== 2/7 [fresh] my 20 testnet steps, traced to the wei from the public RPC";   $PY hands_on.py
echo "== 3/7 [fresh] out of sample: every fee after block 24667602 vs the formula"; $PY fresh_check.py
echo "== 4/7 [saved tx details unless REFRESH=1] every forwarder fee + 15% payout"; if [ "$TO" = latest ]; then $PY fetch_history.py $R; else $PY fetch_history.py --to-block "$TO" $R; fi
echo "== 5/7 0.25% USDr fee check (uses the payout list from step 4)";             $PY check_token_fee.py
echo "== 6/7 [fresh] address types from the explorer";                             $PY check_addresses.py
echo "== +   [fresh] mainnet chain fee split (needs foundry cast)";                (command -v cast >/dev/null && bash check_fee_split.sh 14858726) || echo "skip: cast not installed"
echo "== 7/7 charts";                                                              $PY make_charts.py
echo "done: see ../evidence and ../charts"

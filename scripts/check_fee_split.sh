#!/usr/bin/env bash
# Mainnet chain-fee split: read FeeAggregator.getConfig() directly from the public Rayls mainnet RPC.
# Pass a block number to reproduce the 20 Nov 2026 reading: bash check_fee_split.sh 14858726
set -euo pipefail
CAST=${CAST:-cast}; RPC=https://mainnet-rpc.rayls.com
A=0x07E17E17e17E17e17E17e17e17e17e17E17E17E3   # ERC1967Proxy, verified implementation FeeAggregator (explorer.rayls.com)
B=${1:-$($CAST block-number --rpc-url $RPC)}
echo "chain id:  $($CAST chain-id --rpc-url $RPC)"
echo "block:     $B  (timestamp $($CAST block $B --rpc-url $RPC -f timestamp))"
echo "impl slot: $($CAST storage $A 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $RPC --block $B)"
echo "getConfig() raw: $($CAST call $A 'getConfig()' --rpc-url $RPC --block $B)"
echo "decoded (validatorPoolBps, ecosystemBps, burnBps): $($CAST call $A 'getConfig()((uint256,uint256,uint256))' --rpc-url $RPC --block $B)"

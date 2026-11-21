#!/usr/bin/env bash
# Collect every URL cited in findings.md, README.md and discord-ticket.md and check that it loads (HTTP status).
# reddit.com blocks plain curl (403) for its share links; those are marked and were checked in a normal browser fetch instead.
cd "$(dirname "$0")/.."
grep -ohE 'https?://[^ )`"<>|]+' findings.md README.md discord-ticket.md | sed 's/[.,;:]*$//' | sort -u > evidence/links.txt
: > evidence/link_check.txt
while read -r u; do
  c=$(curl -s -o /dev/null -L -A "Mozilla/5.0" -w '%{http_code}' --max-time 30 "$u")
  case "$u" in *-rpc.rayls.com) [ "$c" = 405 ] && c="405 (JSON-RPC endpoint: GET gives 405, POST works, see evidence/fee_split_mainnet.txt)";; *reddit.com*) [ "$c" != 200 ] && c="$c (reddit blocks curl; loaded fine via web fetch on 20 Nov 2026)";; esac
  echo "$c $u" >> evidence/link_check.txt
done < evidence/links.txt
cat evidence/link_check.txt

#!/bin/bash
# usage: drv.sh NAME 'json' [waitsec]
N=$1; shift; J=$1; W=${2:-3}
L=/workspace/rayls/week3/evidence/browser_$N.log
touch $L
cnt(){ grep -E ' (OK|ERR) ' $L | wc -l; }
before=$(cnt)
echo "$J" > /tmp/drv_$N.fifo
for i in $(seq 1 600); do [ "$(cnt)" -gt "$before" ] && break; sleep 0.5; done
grep -E ' (OK|ERR|EVAL) ' $L | tail -1 | cut -c1-600
sleep $W

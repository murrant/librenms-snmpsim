#!/bin/sh
SCRIPT=$(readlink -f "$0")
SWD=$(dirname "$SCRIPT")

snmpsimd.py --data-dir=$SWD/captures --agent-udpv4-endpoint=127.0.0.1:1161 > /dev/null

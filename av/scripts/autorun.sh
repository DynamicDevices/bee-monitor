#!/bin/sh

if [[ -z "${AUTORUN}" ]]; then
 ./sleep.sh
else
 ./stream.py
fi

#!/bin/sh

if [[ -z "${AUTORUN}" ]]; then
 ./sleep.sh
else
 ./readandpublish.py
fi

#!/bin/bash

source ~/jw_autofill_venv/bin/activate
export TMPDIR=/home/$USER/jw_accounting_tmp
mkdir -p /home/$USER/jw_accounting_tmp
python src/start.py "$@"

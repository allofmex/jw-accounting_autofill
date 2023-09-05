#!/bin/bash

export TMPDIR=/home/$USER/jw_accounting_tmp
mkdir -p /home/$USER/jw_accounting_tmp
python src/start.py "$@"
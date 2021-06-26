#!/usr/bin/env bash

cd /home/pi/repos/bpstatstracker
. venv/bin/activate
python track_meds.py &

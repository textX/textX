#!/bin/bash
mkdir -p reports
python --version > reports/${1}_speed_report.txt 2>&1
python test_speed.py >> reports/${1}_speed_report.txt


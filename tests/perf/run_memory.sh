#!/bin/bash
mkdir -p reports

python --version > reports/${1}_memory_report_nomemoization.txt 2>&1 
python test_memory_nomemoization.py >> reports/${1}_memory_report_nomemoization.txt

python --version > reports/${1}_memory_report_memoization.txt 2>&1 
python test_memory_memoization.py >> reports/${1}_memory_report_memoization.txt

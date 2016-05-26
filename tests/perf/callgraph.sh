#!/bin/bash

# No memoization
python -m cProfile -o reports/${1}_nomemoization_profile.pstats -s time test_callgraph_nomemoization.py
gprof2dot -f pstats reports/${1}_nomemoization_profile.pstats | dot -Tpdf -o reports/${1}_callgraph_nomemoization.pdf

# Memoization
python -m cProfile -o reports/${1}_memoization_profile.pstats -s time test_callgraph_memoization.py
gprof2dot -f pstats reports/${1}_memoization_profile.pstats | dot -Tpdf -o reports/${1}_callgraph_memoization.pdf

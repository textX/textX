#!/bin/bash
python -m cProfile -o profile.pstats -s time light.py
gprof2dot -f pstats profile.pstats | dot -Tpdf -o callgraph.pdf

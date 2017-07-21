#!/bin/sh
export FF_ROOT=$(dirname $0)
export PYTHONWARNINGS=ignore
python3 -m unittest discover tests -s .

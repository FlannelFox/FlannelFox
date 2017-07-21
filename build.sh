#!/bin/sh

python setup.py sdist
rm -fR flannelfox.egg-info
read -p 'Press [Enter] to finish...'
pause
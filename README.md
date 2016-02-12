flannelfox
========

This repo contains a custom set of scritps that can be used to monitor multiple RSS feeds and
search through them for titles you desire. This README will get more info as I get time to
add it.

Warning
========
This repo is not complete as of yet, I still have more to build into the install before it
will work. You have been warned.

Requirements/Dependencies
=========================
Python 2.7
* requests
* beautifulsoup4
* chardet
* pyOpenSSL
* ndg-httpsclient
* pyasn1


Setup
=====

Create .local to install as a user
==================================
mkdir -p ~/.local/lib/python2.7/site-packages

Add ~/.local/bin to your path
=============================
Unix: add `export PATH=$PATH:~/.local/bin` to your ~/.bashrc file
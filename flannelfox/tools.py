# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

def dictMerge(a, b):
	'''
	updates a with b recursively
	'''
	if (
		not isinstance(a, dict) or
		not isinstance(b, dict)
	):
		raise TypeError

	for key in b:
		if key in a:
			if isinstance(a[key], dict) and isinstance(b[key], dict):
				dictMerge(a[key], b[key])
			else:
				a[key] = b[key]
		else:
			a[key] = b[key]
	return a



def changeCharset(data, charset="utf-8", type="xml"):
	'''
	Used to change the character set of a string to the desired format

	data: The text to be converted
	charset: The format the text should be returned in
	type: The engine to be used to convert the charset

	Returns the text after converted
	'''

	if charset is None:
		charset = 'utf-8'

	try:
		data = BeautifulSoup(data, type)
		data = data.encode(encoding=charset, errors="xmlcharrefreplace")

	except Exception as e:
		data = ''

	return data


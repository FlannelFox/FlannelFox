#!/usr/bin/env python3
'''
Borrowed from https://github.com/rakshasa/rtorrent-vagrant/blob/master/scripts/xmlrpc2scgi.py

Allows our script to directly communicate with the rtorrent socket instead
of needing a webserver.

EX.
xmlrpc2scgi.py -p scgi:///home/deerocket/.config/rtorrent/socket system.listMethods
'''


import sys, cStringIO as StringIO
import xmlrpclib, urllib, urlparse, socket

from urlparse import uses_netloc
uses_netloc.append('scgi')

def do_scgi_xmlrpc_request(host, methodname, params=()):
	xmlreq = xmlrpclib.dumps(params, methodname)
	xmlresp = SCGIRequest(host).send(xmlreq)
	return xmlresp

def do_scgi_xmlrpc_request_py(host, methodname, params=()):
	xmlresp = do_scgi_xmlrpc_request(host, methodname, params)
	return xmlrpclib.loads(xmlresp)[0][0]

class SCGIRequest(object):

	def __init__(self, url):
		self.url=url
		self.resp_headers=[]

	def __send(self, scgireq):
		scheme, netloc, path, query, frag = urlparse.urlsplit(self.url)
		host, port = urllib.splitport(netloc)

		if netloc:
			addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
			assert len(addrinfo) == 1, "There's more than one? %r"%addrinfo
			sock = socket.socket(*addrinfo[0][:3])
			sock.connect(addrinfo[0][4])
		else:
			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			sock.connect(path)
		sock.send(scgireq)
		recvdata = resp = sock.recv(1024)

		while recvdata != '':
			recvdata = sock.recv(1024)
			resp += recvdata
		sock.close()
		return resp

	def send(self, data):
		"Send data over scgi to url and get response"
		scgiresp = self.__send(self.add_required_scgi_headers(data))
		resp, self.resp_headers = self.get_scgi_resp(scgiresp)
		return resp

	@staticmethod
	def encode_netstring(string):
		"Encode string as netstring"
		return '%d:%s,'%(len(string), string)

	@staticmethod
	def make_headers(headers):
		"Make scgi header list"
		return '\x00'.join(['%s\x00%s'%t for t in headers])+'\x00'

	@staticmethod
	def add_required_scgi_headers(data, headers=[]):
		"Wrap data in an scgi request,\nsee spec at: http://python.ca/scgi/protocol.txt"
		headers = SCGIRequest.make_headers([('CONTENT_LENGTH', str(len(data))),('SCGI', '1'),] + headers)
		enc_headers = SCGIRequest.encode_netstring(headers)
		return enc_headers+data

	@staticmethod
	def gen_headers(file):
		"Get header lines from scgi response"
		line = file.readline().rstrip()

		while line.strip():
			yield line
			line = file.readline().rstrip()

	@staticmethod
	def get_scgi_resp(resp):
		"Get xmlrpc response from scgi response"
		fresp = StringIO.StringIO(resp)
		headers = []

		for line in SCGIRequest.gen_headers(fresp):
			headers.append(line.split(': ', 1))

		xmlresp = fresp.read()
		return (xmlresp, headers)

class RTorrentXMLRPCClient(object):

	def __init__(self, url, methodname=''):
		self.url = url
		self.methodname = methodname

	def __call__(self, *args):
		scheme, netloc, path, query, frag = urlparse.urlsplit(self.url)
		xmlreq = xmlrpclib.dumps(args, self.methodname)

		if scheme == 'scgi':
			xmlresp = SCGIRequest(self.url).send(xmlreq)
			return xmlrpclib.loads(xmlresp)[0][0]
		elif scheme == 'http':
			raise Exception('Unsupported protocol')
		elif scheme == '':
			raise Exception('Unsupported protocol')
		else:
			raise Exception('Unsupported protocol')

	def __getattr__(self, attr):
		methodname = self.methodname and '.'.join([self.methodname,attr]) or attr
		return RTorrentXMLRPCClient(self.url, methodname)

def convert_params_to_native(params):
	"Parse xmlrpc-c command line arg syntax"
	cparams = []

	for param in params:
		if len(param) < 2 or param[1] != '/':
			cparams.append(param)
			continue
		if param[0] == 'i':
			ptype = int
		elif param[0] == 'b':
			ptype = bool
		elif param[0] == 's':
			ptype = str
		else:
			cparams.append(param)
			continue
		cparams.append(ptype(param[2:]))

	return tuple(cparams)

def print_script(response):
        for line in response:
                print " ".join(map(str, line))

def main(argv):
        if len(argv) < 1:
                print "No arguments."
                raise SystemExit, -1

        if len(argv[0]) and argv[0][0] == '-':
                output_arg = argv[0]
	        argv.pop(0)

        if len(argv) < 2:
                print "Too few arguments."
                raise SystemExit, -1

	host, methodname = argv[:2]
	respxml = do_scgi_xmlrpc_request(host, methodname, convert_params_to_native(argv[2:]))

	if output_arg == '-p':
		print xmlrpclib.loads(respxml)[0][0]
	elif output_arg == '-s':
		print_script(xmlrpclib.loads(respxml)[0][0])
	else:
		print respxml

if __name__ == "__main__":
	main(sys.argv[1:])

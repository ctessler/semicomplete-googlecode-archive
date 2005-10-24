#!/usr/local/bin/python

import SocketServer, BaseHTTPServer
from threading import Thread,Event
from pysqlite2 import dbapi2 as sqlite
import xmlrpclib

import Queue
import re

import socket
import signal
import sys
import os
import time
import random

MEDIAPATH = "/mnt/Audio/MP3"

events = Queue.Queue()
streamlist = {}
clientlist = []

class RPC:
	ofunc = None
	def call(self, method, params, ofunc):
		self.ofunc = ofunc
		func = getattr(self, "call_%s" % method, self.invalidcall)
		func(params)
	
	def respond(self, args):
		m = xmlrpclib.Marshaller()
		self.ofunc("<methodResponse>")
		m.dump_struct(args, self.ofunc)
		self.ofunc("</methodResponse>")

	def call_control(self, params):
		print "CONTROL"
		hash = {
			"result": str(int(params[0]["p1"]) + int(params[0]["p2"]))
		}
		self.respond(hash)

	def call_search(self, params):
		m = MusicList()
		results = {}
		query = params[0]["any"].split(" ");
		results = m.search_allfields(query)
		self.respond(results)
	
	def invalidcall(self, params, ofunc):
		print "Invalid call"
		print "Params: ", params

class MusicList:
	needinit = 0

	def __init__(self):
		self.dbpath = "%s/.pimpdb" % os.getenv("HOME")
		if not os.path.isfile(self.dbpath):
			self.needinit = 1

		self.db = sqlite.connect(self.dbpath, detect_types=sqlite.PARSE_DECLTYPES)

		if self.needinit:
			self.initdb()
			self.findmusic()

	def initdb(self):
		print "Creating database..."
		cur = self.db.cursor()
		cur.execute("""
			CREATE TABLE music (
				songid INTEGER PRIMARY KEY,
				artist VARCHAR,
				album VARCHAR,
				title VARCHAR,
				genre VARCHAR,
				filename VARCHAR
			)
		""")
		cur.close()

	def findmusic(self):
		print "Finding music in %s" % MEDIAPATH
		cur = self.db.cursor()
		os.path.walk(MEDIAPATH, self._findmusic, cur)
		cur.close()
		self.db.commit()

	def _findmusic(self, arg, dirname, fnames):
		cur = arg
		print "Dir: %s" % dirname
		songs = map(lambda x: "%s/%s" % (dirname, x), 
						filter(lambda x: x[-4:] == ".mp3", fnames))
		for s in songs:
			cur.execute("INSERT INTO music (filename) VALUES (:song)", {"song":s})

	def find_randomsong(self):
		cur = self.db.cursor()

		# XXX: Cache this.
		cur.execute("SELECT count(*) FROM music")
		rows = cur.fetchone()

		row = random.randint(0, rows[0] - 1)
		print "SELECT * FROM music LIMIT %d,1"%row
		cur.execute(u"SELECT * FROM music LIMIT %d,1" %row)
		song = cur.fetchone()
		cur.close()
		return song
	
	def search_allfields(self, args):
		cur = self.db.cursor()
		fields = ["artist", "album", "title", "filename"]
		query = "SELECT songid,%s as 'Filename' FROM music WHERE " % ",".join(fields)

		expression = "(%s)" % " OR ".join(map(lambda x: "%s LIKE ?" % x, fields))
		query += " AND ".join(map(lambda x: expression, args))
		query += " LIMIT 30"

		# Can you read this? ;)
		binds = []
		map(lambda x: binds.extend(map(lambda y: "%%%s%%" % x, fields)), args)
		cur.execute(query, binds)
		
		inc = 0
		results = {}
		for i in cur.fetchall():
			entry = {
				"songid": str(i[0]),
				"artist": str(i[1]),
				"album": str(i[2]),
				"title": str(i[3]),
				"filename": str(i[4]),
			}
			#results.append(entry)
			results[str(inc)] = entry
			inc += 1

		return results

class MP3Client:
	def __init__(self, plug):
		self.plug = plug
		self.request = plug.request
		self.output = self.request.wfile
		(self.myhost, self.myport) = self.request.request.getsockname()
		(self.yourhost, self.yourport) = self.request.request.getpeername()
		self.myhost = socket.gethostbyaddr(self.myhost)[0]
		self.yourhost = socket.gethostbyaddr(self.yourhost)[0]
		if streamlist.has_key(self.request.path):
			self.stream = streamlist[self.request.path]
		else:
			self.stream = MP3Stream(self.request.path)
			streamlist[self.request.path] = self.stream

	def __str__(self):
		return "%s:%d" % (self.yourhost, self.yourport)

	def respond(self):
		response = []
		response.append("ICY 200 OK") # Standard shoutcast response
		response.append("icy-url: http://%s:%d/%s" 
							 % (self.myhost, self.myport, self.request.path[1:]))
		response.append("icy-name: Pimp 4.0")

		# Send the response header
		self.output.write("%s\n\n" % "\n".join(response))
	
	def broadcast(self):
		clientlist.append(self)
		print "New client: %s" % self
		print map(lambda x: "%s" % x, clientlist)
		self.respond()

		try:
			while 1:
				song = self.stream.currentsong()
				print "%s: %s" % (self, song)
				self.plug.sendfile(song)
				self.stream.nextsong()
		except socket.error:
			print "SERVER: Client %s:%d disconnected or died" \
				% (self.yourhost,self.yourport)
			if clientlist.index(self) > -1:
				clientlist.remove(self)
			else:
				print "Disconnected client not found in client list (UNEXPECTED ERROR)"

class MP3Stream:
	def __init__(self, request, name="Unknown Stream"):
		self.music = MusicList()
		self.clients = []
		self.name = name
		self.song = None

	def addclient(self, client):
		self.clients.append(client)

	def currentsong(self):
		if self.song is None:
			self.nextsong()

		return self.song

	def nextsong(self):
		song = self.music.find_randomsong()
		self.song = song[-1]

class Pimp:#{{{
	def __init__(self):
		self.server = ConnectionHandler()
		self.threads = [self.server]

	def start(self):
		for a in self.threads:
			print "Starting %s thread" % a.getName()
			a.start()

		# Wait for threads to die
		for a in self.threads:
			a.join()
#}}}

class Plug:#{{{
	def __init__(self,request):
		self.request = request
	
	def sendfile(self, src):
		if not os.path.isfile(src):
			return 0

		f = open(src)
		data = f.read(4096)
		while data:
			self.request.wfile.write(data)
			data = f.read(4096)
#}}}
class RedirectPlug(Plug):#{{{
	def process(self):
		r = self.request
		r.send_response(302)
		r.send_header("Location","/control")
		r.end_headers()
#}}}
class ControlWebPlug(Plug):#{{{
	def process(self):
		r = self.request
		r.send_response(200)
		r.send_header("Content-type", "text/html")
		r.end_headers()

		if r.command == "GET":
			self.sendfile("content/index.html")
#}}}
class ControlXMLRPCPlug(Plug):#{{{
	def process(self):
		r = self.request
		data = r.rfile.read(int(r.headers["content-length"]))
		(params, method) = xmlrpclib.loads(data)

		r.send_response(200)
		r.send_header("Content-type", "text/xml")
		r.end_headers()

		rpc = RPC()
		rpc.call(method, params, r.wfile.write)


#}}}
class GenerateContentPlug(Plug):#{{{
	def process(self):
		r = self.request

#}}}
class StreamPlug(Plug):#{{{
	def process(self):
		client = MP3Client(self)
		client.broadcast()

#}}}
class Error404Plug(Plug):#{{{
	def process(self):
		r = self.request
		r.send_response(404)
		r.send_header("Content-type", "text/html")
		r.end_headers()
		
		if r.command == "GET":
			self.sendfile("content/404.html")
#}}}
class SendContentPlug(Plug):#{{{
	content_type = {
		"css": "text/css",
		"html": "text/html",
		"js": "text/javascript",
		"jpg": "image/jpeg",
		"png": "image/png",
	}

	def process(self):
		r = self.request
		path = "/".join(r.path.split("/")[1:])
		print "PATH: %s" % path

		if path.find("..") > -1:
			Error404Plug(r).process()
			return
		if not os.path.isfile(path):
			Error404Plug(r).process()
			return

		ext = path.split(".")[-1]
		ctype = self.content_type.has_key(ext) \
			and self.content_type[ext] or "text/plain"
		r.send_response(200)
		r.send_header("Content-type", ctype)
		r.end_headers()

		if r.command == "GET":
			self.sendfile(path)
#}}}

class ConnectionHandler(Thread):#{{{
	"""Handle connections from clients. Pass them off to the appropriate handler """

	def __init__(self, port=8000):
		self.port = port
		self.done = False
		self.server = SocketServer.ThreadingTCPServer(('', self.port),
																	 self.RequestHandler)
		Thread.__init__(self,name="ConnectionHandler")

	def run(self):
		while not self.done:
			self.server.handle_request()

	def join(self,timeout=None):
		Thread.join(self, timeout)

	class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		""" HTTP connection handler """

		handlers = {
			'404': Error404Plug,
			'': RedirectPlug,
			'control': ControlWebPlug,
			'xmlrpc': ControlXMLRPCPlug,
			'content': SendContentPlug,
			'generate': GenerateContentPlug,
			'stream': StreamPlug,
		}


		def do_GET(self):
			plug = self.path.split("/")[1]
			if self.handlers.has_key(plug):
				handler = self.handlers[plug](self)
				handler.process()
			else:
				self.handlers['404'](self).process()

		def do_POST(self):
			self.do_GET()

		def do_HEAD(self):
			self.do_GET()
#}}}

def decode_string(val):
	return unicode(val, "US-ASCII").decode("UTF-8")

def adapt_string(val):
	return unicode(val).encode("US-ASCII")

if __name__ == '__main__':
	# Unicode sucks, use ASCII
	sqlite.register_adapter(str, adapt_string)
	sqlite.register_converter('VARCHAR', decode_string)
	m = MusicList()
	p = Pimp()
	p.start()

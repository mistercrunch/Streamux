#!/usr/bin/python
import socket,struct,time,threading,sys
from datetime import datetime
from uuid import getnode as get_mac


MAC 				= get_mac()
UDP_IP 				= '225.0.0.250'
UDP_PORT 			= 8123
POKE_INTERVAL		= 5

class Listener(threading.Thread):
	def __init__(self):
		self.msg = ""
		threading.Thread.__init__(self)
		self.daemon = True
		
	def run(self):
		addrinfo = socket.getaddrinfo(UDP_IP, None)[0]
		s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
		
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('', UDP_PORT))
		group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
		mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
		s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		#s.settimeout(1)
		print("Listening!")
		#last_id_sent = float(datetime.now().strftime('%s.%f'))
		while True:
			try:
				data, sender = s.recvfrom(1500)
			except:
				pass
			else:
				while data[-1:] == '\0':
					data = data[:-1] # Strip trailing \0'
				self.msg = sender[0] + ':' + data

class node(threading.Thread):	
	def __init__(self):
		self.nodes = {}
		threading.Thread.__init__(self)
		self.daemon = True
		
	def send_msg(self, msg):
		addrinfo = socket.getaddrinfo(UDP_IP, None)[0]
		ttl_bin = struct.pack('@i', 1) # Increase to reach other networks
		s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
		s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
		s.sendto(msg + '\0', (addrinfo[4][0], UDP_PORT))
		#Networking setup
		
	def run(self):
		l = Listener()
		l.start()
		last_id_sent = 0
		while True:
			if l.msg:
				if not l.msg.split(':')[1] in self.nodes:
					self.nodes[l.msg.split(':')[1]] = {'IP':l.msg.split(':')[0]}
				l.msg = ""
				
			if last_id_sent + POKE_INTERVAL < float(datetime.now().strftime('%s.%f')):
				self.send_msg(str(MAC) + ':HELLO')
				last_id_sent = float(datetime.now().strftime('%s.%f'))
				
			#print float(datetime.now().strftime('%s.%f'))
			time.sleep(0.1)

n = node()
n.start()

start_webserver = False

if len(sys.argv) > 1:
	if sys.argv[1] == "webserver":
		start_webserver = True
		
if start_webserver:
	import cherrypy
	class root:
		
		def json(self):
			return repr(n.nodes)
		json.exposed = True
		
		def jquery(self):
			return open('templates/jquery-1.7.1.min.js')
		jquery.exposed = True
		
		def index(self):
			return open('templates/index.html')
		index.exposed = True
	cherrypy.quickstart(root())
else:
	while True:
		time.sleep(0.1)
	
					
			
		
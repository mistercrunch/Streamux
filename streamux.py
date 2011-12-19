#!/usr/bin/python
import socket,struct,time,threading,sys
from datetime import datetime
from uuid import getnode as get_mac



UDP_IP 				= '225.0.0.250'
UDP_PORT 			= 8123
POKE_INTERVAL		= 5

keep_msg			= 10

class Listener(threading.Thread):
	def __init__(self):
		self.msg = []
		threading.Thread.__init__(self)
		self.daemon = True
		self.latest_messages = []
		
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
				msg = data.split(':')
				msg.insert(0, sender[0])
				msg.insert(0, str(datetime.now()))
				
				self.latest_messages.insert(0,msg)
				self.latest_messages = self.latest_messages[:keep_msg]
				self.msg = msg
				


class node(threading.Thread):	
	def __init__(self):
		self.nodes = {}
		self.is_on = False
		self.mac = str(get_mac())
		self.is_bcast = False
		threading.Thread.__init__(self)
		self.daemon = True
		self.last_id_sent=0
		
	def send_msg(self, msg):
		addrinfo = socket.getaddrinfo(UDP_IP, None)[0]
		ttl_bin = struct.pack('@i', 1) # Increase to reach other networks
		s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
		s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
		s.sendto(msg + '\0', (addrinfo[4][0], UDP_PORT))
		#Networking setup
		
	def send_info(self):
		self.send_msg(self.mac + ':NODE_INFO:' + str(self.is_on) + ':' + str(self.is_bcast))
		self.last_id_sent = float(datetime.now().strftime('%s.%f'))	
	
	def send_mute(self, mute_mac):
		self.send_msg(self.mac + ':MUTE_NODE:' + str(mute_mac))
		
	def send_unmute(self, mute_mac):
		self.send_msg(self.mac + ':UNMUTE_NODE:' + str(mute_mac))
		
	def mute_node(self):
		self.is_on = False
	
	def unmute_node(self):
		self.is_on = True
		
	def run(self):
		self.l = Listener()
		self.l.start()
		last_id_sent = 0
		while True:
			if self.l.msg:
				msg = self.l.msg
				self.l.msg = ""
				if len(msg)>=2:
					if msg[3] == "NODE_INFO" and len(msg)>=6:
						self.nodes[msg[2]] = {'IP':msg[1], 'IS_ON':msg[4], 'IS_BCAST':msg[5]} 
					elif msg[3] == "MUTE_NODE" and len(msg)>=3:
						if msg[4] == self.mac: self.mute_node()
					elif msg[3] == "UNMUTE_NODE" and len(msg)>=3:
						if msg[4] == self.mac: self.unmute_node()
				
			if self.last_id_sent + POKE_INTERVAL < float(datetime.now().strftime('%s.%f')):
				self.send_info()
				
			#print float(datetime.now().strftime('%s.%f'))
			time.sleep(0.1)

n = node()
n.start()

start_webserver = False

if len(sys.argv) > 1:
	if sys.argv[1] == "webserver":
		start_webserver = True
		
if start_webserver:
	import cherrypy,json
	class root:
		
		def json_nodes(self):
			return json.dumps(n.nodes)
		json_nodes.exposed = True
		
		def json_messages(self):
			return json.dumps(n.l.latest_messages)
		json_messages.exposed = True
		
		def mute_node(self, mac):
			n.send_mute(mac)
			return mac + ' muted'
		mute_node.exposed = True
		
		def unmute_node(self, mac):
			n.send_unmute(mac)
			return mac + ' unmuted'
		unmute_node.exposed = True
		
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
	
					
			
		
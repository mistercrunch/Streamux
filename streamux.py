#!/usr/bin/python
import socket,struct,time,threading,sys
from datetime 	import datetime
from uuid 		import getnode as get_mac
import subprocess
import zmq
import pygst
pygst.require("0.10")
import gst

#-----------------------------------------------
# Network config
#-----------------------------------------------
UDP_IP 				= '224.1.1.1'
UDP_PORT 			= 5000
MUSIC_UDP_PORT		= UDP_PORT + 1
POKE_INTERVAL		= 2
HTTP_PORT			= 8999

keep_msg			= 10
zmq_context 		= zmq.Context()
#-----------------------------------------------

class listener(threading.Thread):
	def __init__(self):
		self.msg_queue = []
		threading.Thread.__init__(self)
		self.daemon = True
		self.latest_messages = []
	
	def msg(self):
		if len(self.msg_queue) >= 1:
			return self.msg_queue.pop()
		
	def run(self):
		
		socket = zmq_context.socket(zmq.SUB)

		socket.connect ("epgm://"+ UDP_IP +":" + str(UDP_PORT))
		socket.setsockopt(zmq.SUBSCRIBE,'')
		
		while True:
			data = socket.recv()
			msg = data.split(':')
			msg.insert(0, str(datetime.now()))
			
			self.latest_messages.insert(0,msg)
			self.latest_messages = self.latest_messages[:keep_msg]
			self.msg_queue.append(msg)
			


class node(threading.Thread):	
	
	def __init__(self):
		self.nodes = {}
		self.stream_process = None
		self.play_process = None
		self.is_on = False
		self.mac = str(get_mac())
		self.pipeline_out = None
		self.pipeline_in = None
		print("MAC:" + self.mac + " listening")
		self.is_bcast = False
		threading.Thread.__init__(self)
		self.daemon = True
		self.last_id_sent=0
		
		self.socket = zmq_context.socket(zmq.PUB)
		self.socket.bind("epgm://"+ UDP_IP +":" + str(UDP_PORT))

		
	def send_msg(self, msg):
		self.socket.send(msg)
		
	def start_streaming(self):
		self.is_bcast = True
		"""
		Equivalent code to this bellow
		cmd = "/usr/bin/gst-launch-0.10 filesrc location=/home/mistercrunch/Code/Streamux/test.mp3 ! mad ! audioconvert ! faac ! rtpmp4apay ! udpsink host="+ stsr(UDP_IP) +" port="+ str(MUSIC_UDP_PORT) + " auto-multicast=true sync=true"
		print cmd
		"""
		#self.stream_process = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE)
		
		self.pipeline_out = gst.Pipeline("pipe_out")
		
		#self.src = gst.element_factory_make("autoaudiosrc", "src")
		self.src = gst.element_factory_make("filesrc", "src")
		self.src.set_property("location", "/home/mistercrunch/Code/Streamux/test.mp3")
		
		self.mad 			= gst.element_factory_make("mad", "sink")
		
		self.audioconvert 	= gst.element_factory_make("audioconvert", "audioconvert")
		
		self.faac 			= gst.element_factory_make("faac", "faac")

		self.rtpmp4apay 	= gst.element_factory_make("rtpmp4apay", "rtpmp4apay")
				
		self.udpsink = gst.element_factory_make("udpsink", "updsink")
		self.udpsink.set_property("host", UDP_IP)
		self.udpsink.set_property("port", MUSIC_UDP_PORT)
		self.udpsink.set_property("auto-multicast", True)
		self.udpsink.set_property("sync", True)
		
		self.pipeline_out.add(self.src, self.mad, self.audioconvert, self.faac, self.rtpmp4apay, self.udpsink)
		gst.element_link_many(self.src, self.mad, self.audioconvert, self.faac, self.rtpmp4apay, self.udpsink)

		self.pipeline_out.set_state(gst.STATE_PLAYING)
		
	def stop_streaming(self):
		self.is_bcast = False
		if self.pipeline_out:
			self.pipeline_out.set_state(gst.STATE_PAUSED)
		
	def send_info(self):
		self.send_msg(self.mac + ':NODE_INFO:' + str(self.is_on) + ':' + str(self.is_bcast))
		self.last_id_sent = float(datetime.now().strftime('%s.%f'))	
	
		
	def unmute_node(self):
		self.is_on = True
		cmd = """/usr/bin/gst-launch-0.10 udpsrc auto-multicast=true multicast-group=225.0.0.250 port=8124 caps="application/x-rtp, media=(string)audio, clock-rate=(int)44100, encoding-name=(string)MP4A-LATM, cpresent=(string)0, config=(string)40002420, payload=(int)96, ssrc=(guint)746617717, clock-base=(guint)4130738665, seqnum-base=(guint)58682" ! gstrtpbin ! rtpmp4adepay ! faad ! alsasink sync=false"""

		self.pipeline_in = gst.Pipeline("pipe_in")
		
		self.udpsrc = gst.element_factory_make("udpsrc", "udpsrc")
		self.udpsrc.set_property("auto-multicast", True)
		self.udpsrc.set_property("multicast-group", UDP_IP)
		self.udpsrc.set_property("port", MUSIC_UDP_PORT)
		self.caps = gst.Caps("application/x-rtp, media=(string)audio, clock-rate=(int)44100, encoding-name=(string)MP4A-LATM, cpresent=(string)0, config=(string)40002420, payload=(int)96, ssrc=(guint)746617717, clock-base=(guint)4130738665, seqnum-base=(guint)58682")
		self.udpsrc.set_property("caps", self.caps)

		self.rtpmp4adepay 	= gst.element_factory_make("rtpmp4adepay", "rtpmp4adepay")
		
		self.faad 			= gst.element_factory_make("faad", "faad")
		
		self.alsasink = gst.element_factory_make("alsasink", "alsasink")
		self.alsasink.set_property("sync", False)
		
		self.pipeline_in.add(self.udpsrc, self.rtpmp4adepay, self.faad, self.alsasink)
		gst.element_link_many(self.udpsrc, self.rtpmp4adepay, self.faad, self.alsasink)

		self.pipeline_in.set_state(gst.STATE_PLAYING)
		
	def mute_node(self):		
		self.is_on = False
		if self.pipeline_in:
			self.pipeline_in.set_state(gst.STATE_PAUSED)
		
	def run(self):
		self.l = listener()
		self.l.start()
		last_id_sent = 0

		while True:
			msg = self.l.msg()
			if msg:
				if len(msg)>=3:
					if msg[2] == "NODE_INFO" and len(msg)>=5:
						self.nodes[msg[1]] = {'IP':'Unknown', 'IS_ON':msg[3], 'IS_BCAST':msg[4]} 
					else:
						if msg[2] == "MUTE_NODE" and len(msg)>=3:
							if msg[3] == self.mac: self.mute_node()
						elif msg[2] == "UNMUTE_NODE" and len(msg)>=3:
							if msg[3] == self.mac: self.unmute_node()
						elif msg[2] == "START_STREAM" and len(msg)>=3:
							if msg[3] == self.mac: self.start_streaming()
							else: self.stop_streaming()
						elif msg[2] == "STOP_STREAM" and len(msg)>=3:
							if msg[3] == self.mac: self.stop_streaming()
						self.send_info()
						
			if self.last_id_sent + POKE_INTERVAL < float(datetime.now().strftime('%s.%f')):
				self.send_info()

			time.sleep(0.01)

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
			n.send_msg(n.mac + ':MUTE_NODE:' + str(mac))
			return mac + ' muted'
		mute_node.exposed = True
		
		def unmute_node(self, mac):
			n.send_msg(n.mac + ':UNMUTE_NODE:' + str(mac))
			return mac + ' unmuted'
		unmute_node.exposed = True
		
		def start_streaming(self, mac):
			n.send_msg(n.mac + ':START_STREAM:' + str(mac))
			return mac + ' streaming'
		start_streaming.exposed = True
		
		def stop_streaming(self, mac):
			n.send_msg(n.mac + ':STOP_STREAM:' + str(mac))
			return mac + ' stopped streaming'
		stop_streaming.exposed = True
		
		def jquery(self):
			return open('templates/jquery-1.7.1.min.js')
		jquery.exposed = True
		
		def index(self):
			return open('templates/index.html')
		index.exposed = True
		
	global_conf = {
			'global': 		{
			'server.socket_host': '127.0.0.1',
			'server.socket_port': HTTP_PORT,
			'log.screen'		: False,
			'log.access_file'	: 'log/access.log',
			'log.error_file'	: 'log/error.log',
		},
	}
	cherrypy.quickstart(root(), config=global_conf)
else:
	while True:
		time.sleep(0.01)
	
					
			
		
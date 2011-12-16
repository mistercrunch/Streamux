#!/usr/bin/env python

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
import socket,struct,time


UDP_IP 		= '225.0.0.250'
UDP_PORT 	= 8123
MYTTL 		= 1 # Increase to reach other networks

def send_msg(msg):
  addrinfo = socket.getaddrinfo(UDP_IP, None)[0]
  ttl_bin = struct.pack('@i', MYTTL)
  s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
  s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
  s.sendto(msg + '\0', (addrinfo[4][0], UDP_PORT))

class GTK_Main:
	
	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_title("Message Sender")
		window.set_default_size(300, -1)
		window.connect("destroy", gtk.main_quit, "WM destroy")
		vbox = gtk.VBox()
		window.add(vbox)
		self.entry = gtk.Entry()
		vbox.pack_start(self.entry, False, True)
		self.button = gtk.Button("Start")
		self.button.connect("clicked", self.start_stop)
		vbox.add(self.button)
		window.show_all()
		"""
		self.player = gst.element_factory_make("playbin2", "player")
		fakesink = gst.element_factory_make("fakesink", "fakesink")
		self.player.set_property("video-sink", fakesink)
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.connect("message", self.on_message)
		"""
	def start_stop(self, w):
	  send_msg(self.entry.get_text())
								
GTK_Main()
gtk.gdk.threads_init()
gtk.main()

"""
gst-launch-0.10 filesrc location=test.mp3 ! mad ! audioconvert ! faac ! rtpmp4apay ! udpsink host=224.1.1.1 port=5000 auto-multicast=true sync=true

gst-launch-0.10 udpsrc auto-multicast=true multicast-group=224.1.1.1 port=5000 ! "application/x-rtp, media=(string)audio, clock-rate=(int)44100, encoding-name=(string)MP4A-LATM, cpresent=(string)0, config=(string)40002420, payload=(int)96, ssrc=(guint)746617717, clock-base=(guint)4130738665, seqnum-base=(guint)58682" ! gstrtpbin ! rtpmp4adepay ! "audio/mpeg,mpegversion=(int)4,channels=(int)2,rate=(int)44100" ! faad ! alsasink sync=false

"""
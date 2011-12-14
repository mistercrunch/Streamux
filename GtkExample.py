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
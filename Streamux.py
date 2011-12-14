import socket,struct,time
from datetime import datetime
from uuid import getnode as get_mac

MAC 			= get_mac()
UDP_IP 			= '225.0.0.250'
UDP_PORT 		= 8123
MYTTL 			= 1 # Increase to reach other networks
SEND_ID_INTERVAL	= 2

def send_msg(msg):
  addrinfo = socket.getaddrinfo(UDP_IP, None)[0]
  ttl_bin = struct.pack('@i', MYTTL)
  s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
  s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
  s.sendto(msg + '\0', (addrinfo[4][0], UDP_PORT))
  
def main():

	#Networking setup
	addrinfo = socket.getaddrinfo(UDP_IP, None)[0]
	s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', UDP_PORT))
	group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
	mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
	s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	s.settimeout(2)

	print("Listening!")
	#last_id_sent = float(datetime.now().strftime('%s.%f'))
	while True:
		data = None
		try :
			data, sender = s.recvfrom(1500)
			while data[-1:] == '\0':
				data = data[:-1] # Strip trailing \0'
			print sender, data
		except:
			send_msg(repr({'MAC':MAC}))
			time.sleep(0.1)
		
		
	
        #print(data)
		
main()


"""
class node:
  def node():
    self.network_key = ''
  
  def find_buddies(self, sock):
    print "hello?"
    sock.
    
    
    
n=node()
n.find_buddies(sock)
"""
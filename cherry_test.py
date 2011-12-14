import cherrypy
from Streamux import node
import time
n = node()
n.start()

class HelloWorld(object):
    def index(self):
        return "yaman:" + repr(n.nodes)
    index.exposed = True

cherrypy.quickstart(HelloWorld())

time.sleep(5)
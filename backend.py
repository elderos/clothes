import cherrypy
from cherrypy.lib.static import serve_file
import os


class Viewer(object):
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/feed')

    def game(self):
        serve_file(os.path.join('static', 'game.html'))

    @cherrypy.expose
    def feed(self):
        serve_file(os.path.join('static', 'feed.html'))


if __name__ == '__main__':
    cherrypy.server.socket_host = 'localhost'
    cherrypy.server.socket_port = 8111  
    config = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('static')
        }
    }

    viewer = Viewer()

    cherrypy.quickstart(viewer, '', config)
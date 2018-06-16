import cherrypy
from cherrypy.lib.static import serve_file
import os
from argparse import ArgumentParser

def static_path(path):
    return os.path.abspath(os.path.join('static', path))


class Viewer(object):

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/feed')

    def game(self):
        serve_file(static_path('game.html'))

    @cherrypy.expose
    def feed(self):
        serve_file(static_path('feed.html'))


def main(args):
    cherrypy.server.socket_host = 'localhost'
    cherrypy.server.socket_port = args.port
    config = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('static')
        }
    }

    viewer = Viewer()

    cherrypy.quickstart(viewer, '', config)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8111, type=int)

    args = parser.parse_args()
    main(args)

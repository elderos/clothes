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

    @cherrypy.expose
    def game(self):
        return serve_file(static_path('game.html'))

    @cherrypy.expose
    def feed(self):
        return serve_file(static_path('feed.html'))

    @cherrypy.expose(['fetch-feed'])
    @cherrypy.tools.json_out()
    def fetch_feed(self, count=10):
        return [{
            'items': [{
                'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
                'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
            }, {
                'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
                'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
            }],
            'votes': 100,
            'rating': 55,
            'author': '@elderos'
        }] * count


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

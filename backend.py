import cherrypy
from cherrypy.lib.static import serve_file
import os
from argparse import ArgumentParser
import csv
import random


def static_path(path):
    return os.path.abspath(os.path.join('static', path))


class Viewer(object):
    def __init__(self, markup_file='markup_agg.tsv'):
        self.rows = []
        with open(markup_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['GOLDEN:result'] != 'yes':
                    continue
                self.rows.append(row)

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/feed')

    @cherrypy.expose
    def game(self):
        return serve_file(static_path('game.html'))

    @cherrypy.expose
    def feed(self):
        return serve_file(static_path('feed.html'))

    def form_item(self, item_id, image):
        basename, ext = os.path.splitext(image)
        image_link = 'https://ae01.alicdn.com/kf/%(uid)s/-%(ext)s_220x220%(ext)s' % {
            'uid': basename,
            'ext': ext
        }

        return {
            'link': 'https://ru.aliexpress.com/item/-/%s.html' % item_id,
            'image': image_link
        }

    @cherrypy.expose(['fetch-feed'])
    @cherrypy.tools.json_out()
    def fetch_feed(self, count=10):
        resp = []
        for _ in xrange(int(count)):
            row = random.choice(self.rows)
            pair = {
                'items': [
                    self.form_item(row['INPUT:item1_id'], row['INPUT:item1_image']),
                    self.form_item(row['INPUT:item2_id'], row['INPUT:item2_image'])
                ],
                'votes': 0,
                'rating': 0,
                'author': '@elderos'
            }
            resp.append(pair)
        return resp


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

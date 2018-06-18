import cherrypy
from cherrypy.lib.static import serve_file
import os
from argparse import ArgumentParser
import random
from common import connect
import ujson as json
from threading import Lock

pairs_lock = Lock()

def static_path(path):
    return os.path.abspath(os.path.join('static', path))

def load_pairs(conn):
    cursor = conn.cursor()
    cursor.execute('select pair_id, data from pairs;')

    pairs = {}

    while True:
        res = cursor.fetchone()
        if res is None:
            break
        pair_id, jdata = res
        pairs[pair_id] = jdata
    cursor.close()
    return pairs


class Viewer(object):
    def __init__(self):
        cherrypy.log('Start fetching pairs...')
        self.pairs = load_pairs(connect())
        cherrypy.log('All pairs fetched')
        self.ids = list(self.pairs.keys())

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
        resp = []
        for _ in range(int(count)):
            r_key = random.choice(self.ids)
            pair = self.pairs[r_key]
            pair['pair_id'] = r_key
            resp.append(pair)
        return resp

    @cherrypy.expose
    def vote(self, pairid, vote):
        pairid = int(pairid)
        if pairid not in self.pairs:
            cherrypy.HTTPError('Unknown pair id')
            return
        pair = self.pairs[pairid]
        with pairs_lock:
            if vote == 'like':
                pair['votes'] += 1
                pair['likes'] += 1
            elif vote == 'dislike':
                pair['votes'] += 1
            else:
                cherrypy.HTTPError('Unknown vote type')
                return

            conn = connect()
            cursor = conn.cursor()
            try:
                cursor.execute('''
update pairs
set data = %(jdata)s
where pair_id = %(pair_id)s;
''', {'jdata': json.dumps(pair), 'pair_id': int(pairid)})
                conn.commit()
            except:
                conn.rollback()



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

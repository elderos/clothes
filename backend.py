import cherrypy
from cherrypy.lib.static import serve_file
import os
from argparse import ArgumentParser
import random
from common import connect
import ujson as json
from threading import Lock
import uuid

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

    def check_user_id(self):
        cookie = cherrypy.request.cookie
        if 'user-id' not in cookie:
            user_id = str(uuid.uuid4())
            cherrypy.response.cookie['user-id'] = user_id
        else:
            user_id = cookie['user-id']
        return user_id


    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/feed')

    @cherrypy.expose
    def game(self):
        user_id = self.check_user_id()
        return serve_file(static_path('game.html'))

    @cherrypy.expose
    def feed(self):
        user_id = self.check_user_id()
        return serve_file(static_path('feed.html'))

    @cherrypy.expose(['fetch-feed'])
    @cherrypy.tools.json_out()
    def fetch_feed(self, count=10):
        user_id = self.check_user_id()
        resp = []
        count = int(count)
        if count <= 0:
            return cherrypy.HTTPError('Invalid parameter value: count=%s' % count)
        for _ in range(int(count)):
            r_key = random.choice(self.ids)
            pair = self.pairs[r_key]
            pair['pair_id'] = r_key
            resp.append(pair)
        return resp

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vote(self, pairid, vote):
        pairid = int(pairid)
        if pairid not in self.pairs:
            cherrypy.HTTPError('Unknown pair id')
            return

        if vote not in ['like', 'dislike']:
            return cherrypy.HTTPError('Unknown vote type')

        user_id = self.check_user_id()

        pair = self.pairs[pairid]
        with pairs_lock:
            conn = connect()
            cursor = conn.cursor()
            try:
                cursor.execute('''
select vote
from likes
where pair_id = %(pair_id)s
    and cookie_id = %(cookie_id)s;
''')
                row = cursor.fetchone();
                prev_vote = 'none' if row is None else row[0]

                final_vote = vote

                if prev_vote == 'none':
                    if vote == 'like':
                        pair['votes'] += 1
                        pair['likes'] += 1
                    elif vote == 'dislike':
                        pair['votes'] += 1
                elif prev_vote == 'like':
                    if vote == 'like':
                        pass  # do nothing, already liked
                    elif vote == 'dislike':
                        pair['likes'] -= 1
                        pair['votes'] -= 1
                        final_vote = 'none'
                elif prev_vote == 'dislike':
                    if vote == 'like':
                        pair['votes'] -= 1
                        final_vote = 'none'
                    elif vote == 'dislike':
                        pass  # do nothing

                cursor.execute('''
insert into likes (pair_id, cookie_id, vote)
values (%(pair_id)s, %(cookie_id)s, %(vote)s)
on conflict (pair_id, cookie_id) do update
    set vote = %(vote)s;
''', {'pair_id': pairid, 'cookie_id': user_id, 'vote': final_vote})

                cursor.execute('''
update pairs
set data = %(jdata)s
where pair_id = %(pair_id)s;
''', {'jdata': json.dumps(pair), 'pair_id': int(pairid)})
                conn.commit()
                return {'status': final_vote, 'pair_data': pair}
            except Exception as e:
                conn.rollback()
                cherrypy.HTTPError(e.message)


def main(args):
    cherrypy.server.socket_host = 'localhost'
    cherrypy.server.socket_port = args.port
    config = {
        '/': {
            'tools.sessions.on': True,
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

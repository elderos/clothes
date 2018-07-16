from __future__ import absolute_import
from argparse import ArgumentParser
from multiprocessing import Pool, Queue
from bs4 import BeautifulSoup
import requests
import json
import signal
from ..common import connect, init_logger


class Proxy(object):
    __slots__ = ['port', 'ip']

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class QueueItem(object):
    __slots__ = ['queueid', 'method', 'data']

    def __init__(self, queueid, method, data):
        self.queueid = queueid
        self.method = method
        self.data = data


def get_fresh_proxies():
    resp = requests.get(
        'http://pubproxy.com/api/proxy?limit=20&type=http&level=elite&country=RU&https=true'
    )
    jdata = json.loads(resp.text)
    proxies = []
    for item in jdata['data']:
        proxies.append(Proxy(item['ip'], item['port']))
    return proxies


def fill_queue(queue):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
update download_queue
set status = 'taken'
where queueid in (
    select queueid
    from download_queue
    where status = 'none'
    limit %(limit)s
)
returning queueid, method, input_data
    ''', {'limit': 1000})

    rows = cursor.fetchall()

    for row in rows:
        queue_item = QueueItem(row['queueid'], row['method'], row['input_data'])
        queue.put(queue_item)



def main(args):
    log = init_logger('scraper')

    proxies = get_fresh_proxies()
    queue = Queue()

    while True:


    for proxy in proxies:
        print '%s\t%s' % (proxy.ip, proxy.port)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-p', '--processes', type=int, default=50)

    args = parser.parse_args()
    main(args)

from __future__ import absolute_import
from argparse import ArgumentParser
from multiprocessing import Pool, Queue
from bs4 import BeautifulSoup
import requests
import json
import signal
from ..common import connect, init_logger


class QueueItem(object):
    __slots__ = ['queueid', 'method', 'data']

    def __init__(self, queueid, method, data):
        self.queueid = queueid
        self.method = method
        self.data = data



def fetch_queue_buf(limit):
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
    ''', {'limit': limit})

    rows = cursor.fetchall()

    res = []
    for row in rows:
        queue_item = QueueItem(row['queueid'], row['method'], row['input_data'])
        res.append(queue_item)
    return res







def main(args):
    log = init_logger('scraper')

    proxies = get_fresh_proxies()

    pool = Pool(args.processes)

    while True:
        buf = fetch_queue_buf(args.buf_limit)
        if not buf:
            break
        items = pool.map()

    pool.join()
    pool.close()



    for proxy in proxies:
        print '%s\t%s' % (proxy.ip, proxy.port)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-p', '--processes', type=int, default=50)
    parser.add_argument('-b', '--buf-limit', type=int, default=10000)

    args = parser.parse_args()
    main(args)

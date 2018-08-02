from __future__ import absolute_import

from argparse import ArgumentParser
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool

from common import init_logger
from robot.parsers import mapping
from .db_access import PostgresProvider, MockProvider
from .proxies import ProxyDownloader


class Mapper(object):
    def __init__(self, downloader):
        self.downloader = downloader

    def map(self, queue_item):
        parser_name = queue_item.method
        if parser_name not in mapping:
            return None
        parser = mapping[parser_name]
        url = parser.build_url(queue_item.data)

        resp = self.downloader.download(url)
        if not resp:
            return DownloadedItem(None, queue_item, url)

        return DownloadedItem(resp, queue_item, url)


class DownloadedItem(object):
    __slots__ = ['downloaded_data', 'queue_item', 'url']

    def __init__(self, data, item, url):
        self.downloaded_data = data
        self.queue_item = item
        self.url = url


class ParsedItem(object):
    __slots__ = ['queue_item', 'parsed_item']

    def __init__(self, queue_item, parsed_item):
        self.queue_item = queue_item
        self.parsed_item = parsed_item


def parse_items(downloaded_item):
    parser_name = downloaded_item.queue_item.method
    parser = mapping[parser_name]

    item = None
    try:
        item = parser.parse(downloaded_item.downloaded_data)
    except Exception as e:
        log.error('Error while parsing url %s' % downloaded_item.url)
        log.debug(downloaded_item.downloaded_data)
        log.exception(e)
    return ParsedItem(downloaded_item.queue_item, item)


def save_item(parsed_item, db):
    if parsed_item.parsed_item is None:
        db.set_fail(parsed_item.queue_item.queueid)
        return 0
    db.save_item(parsed_item.queue_item.queueid, parsed_item.parsed_item)
    return 1


def main(args):
    if args.test:
        db = MockProvider()
    else:
        db = PostgresProvider()

    downloader = ProxyDownloader(30, use_proxies=not args.no_proxies)

    pool = Pool(args.processes)

    thread_pool = ThreadPool(args.download_threads)

    mapper = Mapper(downloader)

    while True:
        buf = db.fetch_queue_buf(args.buf_limit)
        if not buf:
            break

        log.info('Downloading batch')
        downloaded_items = thread_pool.map(mapper.map, buf)
        log.info('Parsing')
        parsed_items = pool.map(parse_items, downloaded_items)

        log.info('Saving')
        batch_stats = thread_pool.map(lambda x: save_item(x, db), parsed_items)

        log.info('Downloaded %s items (%s/%s success)' % (len(buf), sum(batch_stats), len(buf)))

    thread_pool.close()
    thread_pool.join()

    pool.close()
    pool.join()


if __name__ == '__main__':
    log = init_logger('scraper')
    parser = ArgumentParser()

    parser.add_argument('-p', '--processes', type=int, default=cpu_count())
    parser.add_argument('-d', '--download-threads', type=int, default=50)
    parser.add_argument('-b', '--buf-limit', type=int, default=10000)

    parser.add_argument('-P', '--no-proxies', action='store_true', help='Do not use proxy')

    parser.add_argument('-t', '--test', action='store_true')

    args = parser.parse_args()
    main(args)

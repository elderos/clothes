from __future__ import absolute_import
import json
import random
import requests
from collections import defaultdict
from multiprocessing import Lock
from common import init_logger


log = init_logger('scraper')


class ProxyDownloader(object):
    def __init__(self, min_proxy_count, max_errors=3, use_proxies=True):
        proxies = None
        if use_proxies:
            log.info('Requesting proxy list')
            proxies = self.get_fresh_proxies(min_proxy_count)
            log.info('Total %s proxies found' % len(proxies))
        self.proxies = proxies
        self.proxy_errors = defaultdict(int)
        self.locker = Lock()
        self.max_errors = max_errors
        self.min_proxy_count = min_proxy_count
        self.use_proxies = use_proxies

    def get_random_proxy(self):
        with self.locker:
            return random.choice(self.proxies)

    def set_proxy_fail(self, proxy):
        with self.locker:
            self.proxy_errors[proxy] += 1
            if self.proxy_errors[proxy] > self.max_errors:
                self.proxies.remove(proxy)
            if len(self.proxies) < self.min_proxy_count:
                self.proxies += self.get_fresh_proxies(self.min_proxy_count)

    def set_proxy_success(self, proxy):
        self.proxy_errors[proxy] = 0

    def download(self, url):
        proxy = None
        try:
            sess = requests.Session()
            sess.trust_env = False
            if self.use_proxies:
                proxy = self.get_random_proxy()
                resp = sess.get(url, proxies=proxy.dict4request, timeout=10)
            else:
                resp = sess.get(url, timeout=10)

            if resp.status_code != 200:
                return None

            if self.use_proxies:
                self.set_proxy_success(proxy)

            return resp.text
        except Exception as e:
            if self.use_proxies:
                self.set_proxy_fail(proxy)
            log.exception(e)
            return None

    def get_fresh_proxies(self, count):
        resp = requests.get(
            'http://pubproxy.com/api/proxy?limit=%s&type=http&level=elite&country=RU&https=true' % count
        )
        jdata = json.loads(resp.text)
        proxies = []
        for item in jdata['data']:
            proxies.append(Proxy(item['ip'], item['port']))
        return proxies


class Proxy(object):
    __slots__ = ['port', 'ip', 'dict4request']

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.dict4request = {
            'http': 'http://%s:%s' % (self.ip, self.port),
            'https': 'https://%s:%s' % (self.ip, self.port)
        }

    def __str__(self):
        return self.ip + ':' + str(self.port)

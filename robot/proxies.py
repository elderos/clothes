import json
import random
import requests

class ProxyDownloader(object):
    def __init__(self, min_proxy_count):
        proxies = self.get_fresh_proxies(min_proxy_count)
        self.proxies = proxies
        self.proxy_quality = {}

    def download(self, url):
        proxy = random.choice(self.proxies)
        resp = requests.get(url, proxies=proxy.dict4request)
        if resp.status_code != 200:
            return None
        return resp.text



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

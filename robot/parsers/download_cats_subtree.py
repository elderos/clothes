import urllib
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import sys
import random


class CatDesc(object):
    __slots__ = ['cat_id', 'name', 'translation', 'depth']

    def __init__(self, cat_id, name, translation, depth):
        self.cat_id = cat_id
        self.name = name
        self.translation = translation
        self.depth = depth


def main(args):
    browser = webdriver.Chrome(port=45123)

    stack = [(args.start_url, 0)]

    cat_rx = re.compile(r'^(?:https:)?//ru\.aliexpress\.com/category/(\d+)/([^\.]+)\.html.*')

    downloaded = set()

    while len(stack) > 0:
        url, depth = stack.pop()

        cat_id = cat_rx.search(url).group(1)

        if cat_id in downloaded:
            print '\t'*depth + '  # cat_id %s already downloaded' % cat_id
            continue

        sys.stderr.write('# ' + url + '\n')
        browser.get(url)
        if 'secru.aliexpress.com' in browser.current_url:
            ret_page = urllib.quote(url)
            browser.get('https://login.aliexpress.com/buyer_ru.htm?return=%s&from=lighthouse&random=5C31FBF77EF5B2D8C801D094B50E654F' % ret_page)
            sys.stderr.write('# Please log in\n')
            raw_input('# Press enter to continue')
            stack.append((url, depth))
            continue

        time.sleep(random.randint(1, 2))



        # print browser.page_source

        html = BeautifulSoup(browser.page_source, 'lxml')

        subcats = html.find_all('a', attrs={
            'href': cat_rx,
            'rel': 'follow'
        })

        breadcrumb = html.find(id='aliGlobalCrumb').find('h1')
        translation = breadcrumb.find_all('span')[-1]
        cat_name = cat_rx.search(url).group(2)
        cat_name = cat_name.replace('-', '_')
        print '\t'*depth + "'%(cat_id)s': '%(prefix)s_%(cat_name)s',  # %(translation)s" % {
            'cat_id': cat_id,
            'prefix': args.prefix,
            'cat_name': cat_name,
            'translation': translation
        }

        for tag in subcats:
            child_url = 'https:' + tag['href']
            stack.append((child_url, depth + 1))
        downloaded.add(cat_id)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--start-url', required=True)
    parser.add_argument('-p', '--prefix', required=True)

    args = parser.parse_args()
    main(args)

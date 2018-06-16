import requests
import re
import os
import sys
from multiprocessing import Pool


def download_image(name):
    if os.path.exists(os.path.join('img', name)):
        return

    basename, ext = os.path.splitext(name)

    download_url = 'https://ae01.alicdn.com/kf/%(name)s/%(ext)s_220x220%(ext)s' % {
        'name': basename,
        'ext': ext
    }
    try:
        resp = requests.get(download_url)
        if resp.status_code != 200:
            return

        with open(os.path.join('img', name), 'wb') as f:
            f.write(resp.content)
    except:
        pass


if __name__ == '__main__':
    imgs = []
    for line in sys.stdin:
        imgs.append(line.rstrip())

    pool = Pool(10)
    pool.map(download_image, imgs)

    pool.close()
    pool.join()

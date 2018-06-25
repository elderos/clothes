from argparse import ArgumentParser
import csv
import os
import ujson as json
from common import connect
from multiprocessing.dummy import Pool, Lock


counter = 0
locker = Lock()


def item_from_row(row, itemno):
    img = row['INPUT:item%s_image' % itemno]
    basename, ext = os.path.splitext(img)
    pattern = 'https://ae01.alicdn.com/kf/%(id)s/-%(ext)s_%(size)s%(ext)s'
    small_img = pattern % {
        'id': basename,
        'ext': ext,
        'size': '220x220'
    }
    big_img = pattern % {
        'id': basename,
        'ext': ext,
        'size': '640x640'
    }
    return {
        'item_id': row['INPUT:item%s_id' % itemno],
        'link': 'https://aliexpress.com/item/-/%s.html' % row['INPUT:item%s_id' % itemno],
        'image_small': small_img,
        'image_big': big_img,
    }


def insert(row):
    global counter
    conn = connect()
    conn.autocommit = True
    cursor = conn.cursor()
    jdata = json.loads(row['HINT:text'])
    data = {
        'items': [
            item_from_row(row, 1),
            item_from_row(row, 2),
        ],
        'likes': jdata['likes'],
        'votes': jdata['votes']
    }
    cursor.execute('insert into pairs (data) values (%(jdata)s)', {
        'jdata': json.dumps(data)
    })
    cursor.close()
    conn.close()
    with locker:
        counter += 1
        if (counter + 1) % 10000 == 0:
            print '%s items done' % (counter + 1)


def main(args):
    conn = connect()
    conn.autocommit = True
    cursor = conn.cursor()
    if args.truncate:
        cursor.execute('truncate table pairs;')
    with open(args.file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        pool = Pool(50)
        pool.map(insert, reader)
        # for row in reader:
        #     insert(cursor, row)
    cursor.close()



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('-t', '--truncate', action='store_true')

    args = parser.parse_args()
    main(args)

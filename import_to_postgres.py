from argparse import ArgumentParser
import csv
import os
import ujson as json
from common import connect


def main(args):
    conn = connect()
    conn.autocommit = True
    cursor = conn.cursor()
    if args.truncate:
        cursor.execute('truncate table pairs;')
    with open(args.file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for i, row in enumerate(reader):
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
            if i % 10000 == 9999:
                print('%s items done' % (i + 1))
    cursor.close()



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('-t', '--truncate', action='store_true')

    args = parser.parse_args()
    main(args)

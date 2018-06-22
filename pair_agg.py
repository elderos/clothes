import csv
from argparse import ArgumentParser
import itertools as it
import json

def print_header():
    print('\t'.join([
        'INPUT:item1_id',
        'INPUT:item1_title',
        'INPUT:item1_image',
        'INPUT:item2_id',
        'INPUT:item2_title',
        'INPUT:item2_image',
        'GOLDEN:result',
        'HINT:text'
    ]))


def main(args):
    with open(args.file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [x for x in reader if x['GOLDEN:result'] == '' or x['GOLDEN:result'] is None]
        key_fn = lambda x: (x['INPUT:item1_id'], x['INPUT:item2_id'])
        rows.sort(key=key_fn)
        print_header()
        for key, group in it.groupby(rows, key=key_fn):
            group = list(group)
            pos_score = sum([1 for x in group if x['OUTPUT:result'] == 'yes'])
            total = len(group)
            r = group[0]
            if not r['INPUT:item1_id']:
                continue
            print('\t'.join([
                r['INPUT:item1_id'],
                r['INPUT:item1_title'],
                r['INPUT:item1_image'],
                r['INPUT:item2_id'],
                r['INPUT:item2_title'],
                r['INPUT:item2_image'],
                'yes' if pos_score * 100 / total > 75 else 'no',
                json.dumps({'votes': total, 'likes': pos_score})
            ]))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file', metavar='FILE')

    args = parser.parse_args()
    main(args)
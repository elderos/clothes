import os
import pg8000
import logging
pg8000.paramstyle = 'pyformat'

def connect():
    return pg8000.connect(
        os.getenv('USER', 'site'),
        database='clothing',
        unix_sock='/var/run/postgresql/.s.PGSQL.5432'
    )


def init_logger(name):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fh = logging.FileHandler(name + '_log.txt')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)

    return logger

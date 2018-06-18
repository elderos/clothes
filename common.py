import os
import pg8000
pg8000.paramstyle = 'pyformat'

def connect():
    return pg8000.connect(
        os.getenv('USER', 'site'),
        database='clothing',
        unix_sock='/var/run/postgresql/.s.PGSQL.5432'
    )
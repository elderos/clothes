from __future__ import absolute_import
from common import connect


class QueueItem(object):
    __slots__ = ['queueid', 'method', 'data']

    def __init__(self, queueid, method, data):
        self.queueid = queueid
        self.method = method
        self.data = data


class DataProvider(object):
    def fetch_queue_buf(self, limit):
        raise NotImplementedError('Abstract method')

    def set_fail(self, queueid):
        raise NotImplementedError('Abstract method')

    def save_item(self, queueid, item):
        raise NotImplementedError('Abstract method')


class PostgresProvider(DataProvider):
    def set_fail(self, queueid):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
update download_queue
set status = 'fail'
where queueid = %(queueid)s
        ''', {'queueid': queueid})

        conn.close()

    def save_item(self, queueid, item):
        pass

    def fetch_queue_buf(self, limit):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('''
    update download_queue
    set status = 'taken'
    where queueid in (
        select queueid
        from download_queue
        where status = 'none'
        limit %(limit)s
    )
    returning queueid, method, input_data
        ''', {'limit': limit})

        rows = cursor.fetchall()

        res = []
        for row in rows:
            queue_item = QueueItem(row['queueid'], row['method'], row['input_data'])
            res.append(queue_item)

        conn.close()
        return res


class MockProvider(DataProvider):
    def __init__(self):
        self.items = [QueueItem(12345, 'ae', '32824376118')]

    def fetch_queue_buf(self, limit):
        items = self.items
        self.items = []
        return items

    def set_fail(self, queueid):
        pass

    def save_item(self, queueid, item):
        pass

import os
import random
import uuid
import random
import time

from datetime import datetime
from argparse import ArgumentParser
from threading import Lock
from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def ts(dt):
    return int(time.mktime(dt.timetuple()))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    photo = db.Column(db.Binary(), nullable=True)
    hash = db.Column(db.String(40), unique=False, nullable=True)
    openid = db.Column(db.String(120), unique=False, nullable=True)
    openid_hash = db.Column(db.String(120), unique=False, nullable=True)
    gender = db.Column(db.String(20), unique=False, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    photo = db.Column(db.Binary(), nullable=True)
    small_photo = db.Column(db.Binary(), nullable=True)
    link = db.Column(db.String(256), unique=False, nullable=False)
    category = db.Column(db.String(256), unique=False, nullable=False)
    price = db.Column(db.Float(), unique=False, nullable=False)
 

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_1_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    item_2_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    timestamp = db.Column(db.Integer, unique=False, nullable=False)
    title = db.Column(db.String(256), unique=False, nullable=True)
    text = db.Column(db.String(1256), unique=False, nullable=True)
    photo = db.Column(db.Binary(), nullable=True)


    def __repr__(self):
        return '<User %r>' % self.title

class Subscription(object):
    def __init__(self, user_id, subscriber_id, timestamp):
        self.user_id = user_id
        self.subscriber_id = subscriber_id
        self.timestamp = timestamp

class Save(object):
    def __init__(self, user_id, post_id, timestamp):
        self.user_id = user_id
        self.post_id = post_id
        self.timestamp = timestamp

class Like(object):
    def __init__(self, user_id, post_id, value, timestamp):
        self.user_id = user_id
        self.post_id = post_id
        self.value = value
        self.timestamp = timestamp


subscriptions = db.Table('subscriptions',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('subscriber_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('timestamp', db.Integer, unique=False, nullable=False),
    #db.UniqueConstraint('user_id', 'subscriber_id', name='uc_sc'),
)


saves = db.Table('saves',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable=False),
    db.Column('timestamp', db.Integer, unique=False, nullable=False),
    #db.UniqueConstraint('user_id', 'post_id', name='uc_sv'),
)

likes = db.Table('likes',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable=False),
    db.Column('value', db.Integer, unique=False, nullable=False),
    db.Column('timestamp', db.Integer, unique=False, nullable=False),
    #db.UniqueConstraint('user_id', 'post_id', name='uc_sv'),
)

db.mapper(Subscription, subscriptions)
db.mapper(Save, saves)
db.mapper(Like, likes)

def feed_query(addon='', order='order by post.timestamp desc '):
    return (
        'select post.id, sum(L.value) as S, post.item_1_id, post.item_2_id, post.timestamp, post.user_id, user.name ' +
        'from post ' +
        'join user ' + 
        'on user.id = post.user_id ' +
        'left join likes as L ' +
        'on L.post_id = post.id ' + 
        addon + 
        'group by post.id ' + 
        order +
        'limit %s offset %s'
    )

def fetch_feed(user_id, t, count, position):
    COLUMNS = ['id', 'votes', 'item_1_id', 'item_2_id', 'timestamp', 'user_id', 'user_name']
    if t == 'top':
        query = db.engine.execute((feed_query(order='order by S desc ')) % (count, position))
    elif t == 'random':
        query = db.engine.execute((feed_query()) % (count, position))
    elif t == 'subscriptions':
        query = db.engine.execute((feed_query(
            addon='join subscriptions ' + 
            'on subscriptions.user_id = post.user_id ' + 
            'where subscriptions.subscriber_id = %s ' % user_id,
        )) % (count, position))
    elif t == 'likes':
        query = db.engine.execute((feed_query(
            addon='join likes ' + 
            'on likes.post_id = post.id ' + 
            'where likes.user_id = %s ' % user_id,
            order='order by likes.timestamp desc '
        )) % (count, position))
    elif t == 'posts':
        query = db.engine.execute((feed_query(
            addon='where post.user_id = %s ' % user_id,
        )) % (count, position))
    elif t == 'saves':
        query = db.engine.execute((feed_query(
            addon='join saves ' + 
            'on saves.post_id = post.id ' + 
            'where saves.user_id = %s ' % user_id,
            order='order by saves.timestamp desc '
        )) % (count, position))
    else:
        raise ValueError('Wrong feed type %s' % t)
    res = [{COLUMNS[i]: r for i, r in enumerate(row)} for row in query.fetchall()]
    print res
    pids = ', '.join([str(r['id']) for r in res])
    savs = {row[0]: row[1] for row in db.engine.execute('select post_id, sum(1) from saves where saves.post_id in (%s) group by saves.post_id' % pids)}
    saved = {row[0]: row[1] for row in db.engine.execute('select post_id, 1 from saves where post_id in (%s) and saves.user_id=%s' % (pids, user_id))}
    votes = {row[0]: row[1] for row in db.engine.execute('select post_id, value from likes where post_id in (%s) and likes.user_id=%s' % (pids, user_id))}
    for r in res:
        r['saves'] = savs.get(r['id'], 0)
        r['saved'] = saved.get(r['id'], 0)
        r['vote'] =  votes.get(r['id'], 0)
        r['votes'] = r['votes'] or 0
    return res


def fetch_notifications(user_id, count, position):
    COLUMNS = ['id', 'name', 'timestamp', 'post_id', 'item_1_id', 'item_2_id']
    likes_query = ('select user.id, user.name, likes.timestamp, likes.post_id, post.item_1_id, post.item_2_id ' +
        'from user ' + 
        'join likes ' + 
        'on likes.user_id = user.id ' + 
        'join post ' + 
        'on likes.post_id = post.id ' + 
        'where post.user_id=%s ' % user_id
    )
    subscriptions_query = ('select user.id, user.name, subscriptions.timestamp, Null as post_id, Null as item_1_id, Null as item_2_id ' +
        'from user ' + 
        'join subscriptions ' + 
        'on subscriptions.subscriber_id = user.id ' + 
        'where subscriptions.user_id=%s ' % user_id
    )

    rows = db.engine.execute(
        likes_query + ' Union ' + subscriptions_query + ' order by timestamp desc limit %s offset %s' % (count, position)
    ).fetchall()
    return [{COLUMNS[i]: r for i, r in enumerate(row)} for row in rows]


def fetch_game_column(user_id=None, item_id=None, prev_item_id=None, position=None, count=None):
    if item_id is not None:
        i = Item.query.get(item_id)
        res = fetch_game_column(user_id=user_id, prev_item_id=prev_item_id, position=position, count=count)
        return [i] + [r for r in res if r.id != item_id]
    else:
        return recommender(user_id=user_id, prev_item_id=prev_item_id, position=position, count=count)


def recommender(user_id=None, prev_item_id=None, position=None, count=None):
    query = Item.query
    if prev_item_id is not None:
        cat = Item.query.get(prev_item_id).category
        query = query.filter(Item.category!=cat)
    query = query.limit(count).offset(position)
    return query.all()


def merge_like(user_id, post_id, value):
    t = ts(datetime.utcnow())
    if db.engine.execute('select * from likes where user_id=%s and post_id=%s' % (user_id, post_id)).fetchall():
        db.engine.execute('update likes set value=%s, timestamp=%d where user_id=%s and post_id=%s' % (value, t, user_id, post_id))
    else:
        db.engine.execute(
            'insert into likes (post_id, user_id, value, timestamp) ' +
            'values(%s, %s, %s, %d)' % (post_id, user_id, value, t)
        )
    ''' # PGSQL 
    data = {
        'user_id': user_id,
        'post_id': post_id,
        'value': value,
        'timestamp': ts(datetime.utcnow()),
    }
    db.engine.execute((
        'insert into likes (post_id, user_id, value, timestamp) ' +
        'values(%(user_id)s, %(post_id)s, %(value)s, %(timestamp)d) ' +
        'on conflict(post_id, cookie_id) do ' +
        'update set value=%(value)s, timestamp=%(timestamp)d'
    ) % data)'''


def merge_save(user_id, post_id):
    t = ts(datetime.utcnow())
    if db.engine.execute('select * from saves where user_id=%s and post_id=%s' % (user_id, post_id)).fetchall():
        db.engine.execute('update saves set timestamp=%d where user_id=%s and post_id=%s' % (t, user_id, post_id))
    else:
        db.engine.execute(
            'insert into saves (post_id, user_id, timestamp) ' +
            'values(%s, %s, %d)' % (post_id, user_id, t)
        )

    ''' # PGSQL
    data = {
        'user_id': user_id,
        'post_id': post_id,
        'timestamp': ts(datetime.utcnow()),
    }
    db.engine.execute((
        'insert into saves (post_id, user_id, timestamp) ' +
        'values(%(user_id)s, %(post_id)s, %(timestamp)d) ' +
        'on conflict(post_id, cookie_id) do ' +
        'update set (timestamp=%(timestamp)d)'
    ) % data)
'''

def fv_or_0(rows):
    return rows[0][0] if rows and rows[0] and rows[0][0] else 0


def fetch_votes(user_id, post_id):
    res = {
        'vote': fv_or_0(db.engine.execute('select value from likes where post_id=%s and user_id=%s' % (post_id, user_id)).fetchall()),
        'saved': fv_or_0(db.engine.execute('select 1 from saves where post_id=%s and user_id=%s' % (post_id, user_id)).fetchall()),
        'votes': fv_or_0(db.engine.execute('select sum(value) from likes where post_id=%s' % post_id).fetchall()),
        'saves': fv_or_0(db.engine.execute('select sum(1) from saves where post_id=%s' % post_id).fetchall()),
    }
    return res

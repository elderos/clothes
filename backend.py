import os
import random
import ujson as json
import uuid
import random
import model

from datetime import datetime
from argparse import ArgumentParser
from threading import Lock
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_login import LoginManager, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

FEED_PAGE_SIZE = 10

login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

model.db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return model.User.query.get(int(id))


def get_uid():
    # TODO
    # return request.cookies.get('userID', str(uuid.uuid4()))
    return '1'


def get_item_id(position=1):
    return request.cookies.get('item_%d_ID' % (position), str(uuid.uuid4()))


@app.template_filter()
def timesince(dt, default="just now"):
    dt = datetime.utcfromtimestamp(int(dt))
    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


@app.route('/')
@app.route('/feed')
def feed():
    user_id = get_uid()
    explore = model.fetch_feed(user_id, 'random', FEED_PAGE_SIZE, 0)
    top = model.fetch_feed(user_id, 'top', FEED_PAGE_SIZE, 0)
    subscriptions = model.fetch_feed(user_id, 'subscriptions', FEED_PAGE_SIZE, 0)
    return render_template('feed.html', top=top, explore=explore, subscriptions=subscriptions, feed=top)


@app.route('/fetch-feed/<t>')
def fetch_feed(t):
    user_id = get_uid()
    count = int(request.args.get('count', FEED_PAGE_SIZE))
    position = int(request.args.get('position', 0))
    assert count > 0 and count < 100, 'Invalid parameter value: count=%s' % count

    feed = model.fetch_feed(user_id, t=t, count=count, position=position)
    return render_template('feed_scroll.html', feed=feed)


@app.route('/vote')
def vote():
    user_id = get_uid()
    post_id = int(request.args.get('post_id', None))
    if request.args.get('vote', None) == 'like':
        vote = 1
    elif request.args.get('vote', None) == 'dislike':
        vote = -1
    else:
        vote = 0

    model.merge_like(user_id, post_id, vote)
    return render_template('vote.html', post=model.fetch_votes(user_id, post_id))

@app.route('/save')
def save():
    user_id = get_uid()
    post_id = int(request.args.get('post_id', None))

    model.merge_save(user_id, post_id)
    return render_template('vote.html', post=model.fetch_votes(user_id, post_id))



@app.route('/game')
def game():
    item_id = request.args.get('item_id', None)
    if item_id is not None:
        item_id = int(item_id)
    user_id = get_uid()
    first = model.fetch_game_column(user_id=user_id, item_id=item_id)
    second = model.fetch_game_column(user_id=user_id, prev_item_id=first[0].id)

    return render_template('game.html', column_1=first, column_2=second)


@app.route('/get-game-first')
def get_game_first():
    user_id = get_uid()
    first = model.fetch_game_column(user_id=user_id)
    return render_template('game_column.html', column=first, column_pos=1)


@app.route('/get-game-second')
def get_game_second():
    user_id = get_uid()
    first_id = get_item_id(1)
    second = model.fetch_game_column(user_id=user_id, prev_item_id=first_id)
    return render_template('game_column.html', column=second, column_pos=2)


@app.route('/profile')
def profile():
    user_id = get_uid()
    posts = model.fetch_feed(user_id, 'posts', FEED_PAGE_SIZE, 0)
    likes = model.fetch_feed(user_id, 'likes', FEED_PAGE_SIZE, 0)
    saves = model.fetch_feed(user_id, 'saves', FEED_PAGE_SIZE, 0)
    return render_template('profile.html', user=model.User.query.get(user_id), likes=likes, saves=saves, posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/settings')
def settings():
    user_id = get_uid()
    return render_template('settings.html', user=model.User.query.get(user_id))


@app.route('/notifications')
def notifications():
    user_id = get_uid()
    notifications = model.fetch_notifications(user_id, FEED_PAGE_SIZE, 0)
    return render_template('notifications.html', notifications=notifications)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    user = User(request.form['username'], generate_password_hash(request.form['password']), request.form['email'], request.form['gender'], request.form['age'])
    # TODO
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    # TODO: AUTH:
    # registered_user = User.query.filter_by(username=username, password=generate_password_hash(password)).first()
    # if registered_user is None:
    #    flash('Username or Password is invalid' , 'error')
    #    return redirect(url_for('login'))
    registered_user = User.query.filter_by(username=username).first()
    login_user(registered_user)
    next = request.args.get('next')
    if not flask.is_safe_url(next):
        return flask.abort(400)

    flash('Logged in successfully')
    return redirect(next or url_for('feed'))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/trending')
def trending():
    user_id = get_uid()
    trending = db.fetch_trending(user_id)
    return render_template('trending.html', trending=trending)


@app.route('/item-image/<id>')
def item_image(id):
    i = model.Item.query.filter_by(id=id).first()
    response = make_response(i.photo)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename='%s.jpg' % id)
    return response


@app.route('/user-image/<id>')
def user_image(id):
    i = model.User.query.filter_by(id=id).first()
    response = make_response(i.photo)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename='%s.jpg' % id)
    return response

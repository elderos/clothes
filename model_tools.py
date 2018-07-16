#!/usr/bin/env python

import click
import random
import os
import time

from datetime import datetime, timedelta
from backend import app
from model import db, User, Item, Post, Subscription, Like, Save
from sqlalchemy.exc import IntegrityError
from model_gen_data import USERNAME_1, USERNAME_2, NAME, SURNAME


def ts(dt):
    return int(time.mktime(dt.timetuple()))


def avatar_random(gen_data):
    ava_path = os.path.join(gen_data, 'avatars')
    ava_name = random.choice(list(os.listdir(ava_path)))
    return open(os.path.join(ava_path, ava_name)).read()


def random_item():
    query = Item.query
    row_count = int(query.count())
    return query.offset(int(row_count * random.random())).first()


def random_user():
    query = User.query
    row_count = int(query.count())
    return query.offset(int(row_count * random.random())).first()


def random_post():
    query = User.query
    row_count = int(query.count())
    return query.offset(int(row_count * random.random())).first()


def gen_post(gen_data, days_before, db):
    d = datetime.today() - timedelta(days=days_before)
    current_d = d - timedelta(minutes=random.randint(1200))
    u = random_user()
    i1 = random_item()
    i2 = random_item()

    return Post(
        user_id=u.id,
        item_1_id=i1.id,
        item_2_id=i2.id,
        timestamp=ts(current_d),
    )


def gen_item(gen_data):
    cat_path = os.path.join(gen_data, 'items')
    cat_name = random.choice(list(os.listdir(cat_path)))
    item_path = os.path.join(cat_path, cat_name)
    item_name = random.choice(list(os.listdir(item_path)))
    photo = open(os.path.join(item_path, item_name)).read()

    return Item(
        name=item_name.split()[0],
        photo=photo,
        small_photo=photo,
        link='http://google.com/',
        category=cat_name,
        price=random.random()*100.
    )


def gen_user(path):
    print path
    return User(
        login=(random.choice(USERNAME_1) + random.choice(USERNAME_2)),
        name=(random.choice(NAME) + ' ' + random.choice(SURNAME)),
        email=(random.choice(USERNAME_1) + random.choice(USERNAME_2)).lower() + '@gmail.com',
        photo=avatar_random(path),
    )


def gen_subscription(gen_data, days_before, db):
    d = datetime.today() - timedelta(days=days_before)
    current_d = ts(d - timedelta(minutes=random.randint(1200)))
    u = random_user()
    s = random_user()
    return Subscription(
        u.id,
        s.id,
        current_d,
    )


@click.group()
def cli():
    pass


@click.command()
@click.option('--path', help='path to json with database')
def import_db(path):
    db.drop_all()
    db.create_all()


@click.command()
@click.option('--path', help='path to json for generation database')
@click.option('--gen_data', help='path to static files (gen_data/clothes/$category/$i.jpg - for clothes images)')
@click.pass_context
def generate_db(ctx, path, gen_data):
    with app.app_context():
        db.drop_all()
        db.create_all()

        for i in range(0, 40):
            try:
                db.session.add(gen_user(gen_data))
                db.session.commit()
                print 'Add User'
            except IntegrityError:
                db.session.rollback()
                print 'Rollback User'

        for i in range(0, 40):
            try:
                db.session.add(gen_item(gen_data))
                db.session.commit()
                print 'Add Item'
            except IntegrityError:
                db.session.rollback()
                print 'Rollback Item'

        for i in range(0, 10):
            iterate_day(gen_data, 10 - i)
    return 0


@click.command()
@click.option('--path', help='path to json for generation database')
@click.option('--static', help='path to static files (statis/clothes/$category/$i.jpg - for clothes images)')
def export_db(path, static):
    raise NotImplemented()


def iterate_day(path, days_before):
    d = datetime.today() - timedelta(days=days_before)
    day_posts = []

    # Posting
    for k in range(0, 5):
        u = random_user()
        im_1 = random_item()
        im_2 = random_item()
        current_d = ts(d + timedelta(minutes=random.randint(0, 1200)))
        day_posts.append(Post(u.id, im_1.id, im_2.id, current_d))
        try:
            db.session.add(day_posts[-1])
            db.session.commit()
            print 'Add post'
        except IntegrityError:
            print 'Rollback post'
            db.session.rollback()

    for k in range(0, 7):
        current_d = ts(d + timedelta(minutes=random.randint(0, 1200)))
        u = random_user()
        # liking
        for i in range(0, 3):
            p = random_post()
            try:
                db.session.add(Like(u.id, p.id, 1, current_d))
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            # saving
            if random.randint(0, 5) == 1:
                try:
                    db.session.add(Save(u.id, p.id, current_d))
                except IntegrityError:
                    db.session.rollback()

        # subscribing
        u2 = random_user()
        try:
            db.session.add(Subscription(u.id, u2.id, current_d))
            db.session.commit()
            print 'Add Subscription'
        except IntegrityError:
            print 'Rollback Subscription'
            db.session.rollback()

cli.add_command(import_db)
cli.add_command(export_db)
cli.add_command(generate_db)

if __name__ == '__main__':
    cli()

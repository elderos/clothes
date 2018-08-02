class ParserBase(object):
    def parse(self, text):
        raise NotImplementedError('Abstract method')

    def build_url(self, data):
        raise NotImplementedError('Abstract method')


class Item(object):
    __slots__ = [
        'init_data',
        'source',
        'title',
        'price',
        'currency',
        'img_big',
        'img_small',
        'cat_ids',
        'stock_available',
        'rating',
        'votes',
        'orders',
        'reviews',
        'seller',
        'seller_rating',
        'wishlist_count',
        'delivery_time'
    ]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in Item.__slots__:
                setattr(self, k, v)
            else:
                raise ValueError('Invalid argument: %s' % k)


def default(default_value=None):
    def decorator(func):

        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return default_value
        return new_func
    return decorator

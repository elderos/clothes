const buffer = [{
    items: [{
        'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
        'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
    }, {
        'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
        'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
    }],
    votes: 100,
    rating: 55,
    author: '@elderos'
}, {
    items: [{
        'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
        'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
    }, {
        'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
        'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
    }],
    votes: 88,
    rating: 22,
    author: '@elderos'
}, {
    items: [{
        'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
        'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
    }, {
        'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
        'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
    }],
    votes: 88,
    rating: 22,
    author: '@elderos'
}, {
    items: [{
        'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
        'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
    }, {
        'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
        'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
    }],
    votes: 88,
    rating: 22,
    author: '@elderos'
}, {
    items: [{
        'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
        'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
    }, {
        'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
        'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
    }],
    votes: 88,
    rating: 22,
    author: '@elderos'
}, {
    items: [{
        'link': 'https://ru.aliexpress.com/item/-/32825303424.html',
        'image': 'https://ae01.alicdn.com/kf/HTB1THlsfazB9uJjSZFMq6xq4XXaf/Bobokateer-Vogue.jpg_220x220.jpg'
    }, {
        'link': 'https://ru.aliexpress.com/item/-/32852682510.html',
        'image': 'https://ae01.alicdn.com/kf/HTB18MEDXbSYBuNjSspiq6xNzpXar/-.jpg_220x220.jpg'
    }],
    votes: 88,
    rating: 22,
    author: '@elderos'
}];


function fetch_next(count, callback) {
    $.get('feed/fetch?count' + count,
        null,
        function (data, status, req) {
            for (let i = 0; i < data.length; i++){
                buffer.push(data[i]);
            }
            if (callback) {
                callback();
            }
        },
        'json'
    );
}


function create_item_view(data){
    const link = $('<a>', {
        class: 'feed-post__item-link',
        href: data.link,
    });
    const image = $('<img>', {
        class: 'feed-post__img',
        src: data.image,
        target: '_blank',
    }).appendTo(link);

    return link;
}


function draw_next() {
    if (buffer.length < 2){
        fetch_next(10, draw_next);
    }

    if (buffer.length < 1){
        return false;
    }

    const feed = $('#feed')[0];

    const data = buffer.pop();
    const post = $('<div>', {
        class: 'feed-post',
        data: data,
    });
    post.appendTo(feed);

    const item_container = $('<div>', {
        class: 'feed-post__item-container'
    });
    item_container.appendTo(post);
    for (let i = 0; i < data.items.length; i++){
        const item = data.items[i];
        const view = create_item_view(item);
        view.appendTo(item_container);
    }

    const panel = $('<div>', {
        class: 'feed-post__panel'
    });
    panel.appendTo(post);

    return true;
}


function check_feed_position(){
    const feed = $('#feed')[0];
    let rect = feed.getBoundingClientRect();
    let window_bottom = $(window).scrollTop() + $(window).height();
    while (rect.bottom - window_bottom < 250) {
        if (!draw_next()){
            break;
        }
        rect = feed.getBoundingClientRect();
    }
}


window.addEventListener('load', function () {
    check_feed_position();
});

window.addEventListener('scroll', function (e){
    check_feed_position();
});
const buffer = [];


function fetch_next(count, callback) {
    $.get('fetch-feed?count=' + count,
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
        src: data.image_small,
        target: '_blank',
    }).appendTo(link);

    return link;
}


function draw_next() {
    if (buffer.length < 2){
        fetch_next(10, check_feed_position);
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

    if (feed.children.length > 1000) {
        return false;
    }


    return true;
}


function check_feed_position(){
    const feed = $('#feed')[0];
    let rect = feed.getBoundingClientRect();
    let window_bottom = $(window).scrollTop() + $(window).height();
    while (rect.height - window_bottom < 250) {
        if (!draw_next()){
            break;
        }
        console.log(rect);
        console.log(window_bottom);
        rect = feed.getBoundingClientRect();
    }
}


window.addEventListener('load', function () {
    check_feed_position();
});

window.addEventListener('scroll', function (e){
    check_feed_position();
});
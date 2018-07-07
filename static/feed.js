function create_item_view(data){
    const link = $('<a>', {
        class: 'feed-post__item-link',
        href: data.link,
        target: '_blank'
    });
    const image = $('<img>', {
        class: 'feed-post__img',
        src: data.image_small,
        target: '_blank',
    }).appendTo(link);

    return link;
}


function refresh_score(data, score){
    const final_score = data.likes + (data.likes - data.votes);
    score.innerHTML = final_score > 0 ? '+' + final_score : final_score; 
}


function btn_svg_string(direction, color){
    const points = direction == 'up' ? '0,100 50,0 100,100' : '0,0 50,100 100,0';
    return '<svg viewBox="0 0 100 100" width="100%" height="100%"><polygon points="' + points + '" style="fill:' + color + ';"/></svg>';
}


function refresh_like_btns(status, like_btn, dislike_btn){
    like_btn[0].innerHTML = btn_svg_string('up', 'darkgrey');
    dislike_btn[0].innerHTML = btn_svg_string('down', 'darkgrey');
    if (status == 'like'){
        like_btn[0].innerHTML = btn_svg_string('up', 'lightgreen');
    } else if (status == 'dislike'){
        dislike_btn[0].innerHTML = btn_svg_string('down', 'lightpink');
    }
}


function change_like_status(data, like_btn, score_wrapper, dislike_btn, vote){
    $.get(
        'vote?pairid=' + data.pair_id + '&vote=' + vote,
        null,
        function(answer_data, status, request){
            refresh_like_btns(answer_data.status, like_btn, dislike_btn);
            data.likes = answer_data.pair_data.likes;
            data.votes = answer_data.pair_data.votes;
            refresh_score(data, score_wrapper[0]);
        },
        'json'
    )
}


function create_panel(data){
    const panel = $('<div>', {
        class: 'feed-post__panel'
    });

    const btn_container = $('<div>', {
        class: 'feed-post__panel__btn-container'
    });
    btn_container.appendTo(panel);

    const score_wrapper = $('<div>', {
        class: 'feed-post__panel__score'
    });
    const score = $('<span>', {
        class: 'feed-post__panel__score-text'
    });
    score.appendTo(score_wrapper);
    
    const dislike_link = $('<div>', {
        class: 'feed-post__panel__link feed-post__panel__dislike',
    });
    dislike_link.appendTo(btn_container);

    score_wrapper.appendTo(btn_container);
    refresh_score(data, score[0]);

    const like_link = $('<div>', {
        class: 'feed-post__panel__link feed-post__panel__like',
    });

    like_link.appendTo(btn_container);

    dislike_link.click(function(){
        change_like_status(data, like_link, score, dislike_link, 'dislike');
    });
    like_link.click(function(){
        change_like_status(data, like_link, score, dislike_link, 'like');
    });

    refresh_like_btns(data.status, like_link, dislike_link);

    return panel;
}


function draw_next() {
    const feed = $('.tab-container__active')[0];
    
    const buffer = feed.buffer;

    if (buffer.length < 2){
        fetch_next(feed.url_build_fn, check_feed_position);
    }

    if (buffer.length < 1){
        return false;
    }


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

    const panel = create_panel(data);
    panel.appendTo(post);

    if (feed.children.length > 1000) {
        return false;
    }

    return true;
}


function random_feed_fetch(){
    let url = 'fetch-feed?count=30';
    return url;
}


function fetch_next(url_build_fn, callback) {
    const buffer = $('.tab-container__active')[0].buffer;
    $.get(url_build_fn(),
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


function check_feed_position(){
    const feed = $('.tab-container__active')[0];
    let rect = feed.getBoundingClientRect();
    let window_bottom = $(window).scrollTop() + $(window).height();
    while (rect.height - window_bottom < 250) {
        if (!draw_next()){
            break;
        }
        rect = feed.getBoundingClientRect();
    }
}


function set_tab_active(tab_id, tab_wrapper_id){
    $('.tab-wrapper').removeClass('tab__active');
    $(tab_wrapper_id).addClass('tab__active');
    $('.tab-container').removeClass('tab-container__active');
    const main_tab = $(tab_id);
    main_tab.addClass('tab-container__active');
    check_feed_position();
}


window.addEventListener('load', function () {
    $('#menu-feed-btn').addClass('menu__btn__active');
    $('#random-feed-container')[0].url_build_fn = random_feed_fetch;
    $('#top-feed-container')[0].url_build_fn = random_feed_fetch; //TODO
    $('.tab-container').map(function(x){
        $(this)[0].buffer = [];
    });
    set_tab_active('#random-feed-container', '#tab-wrapper__random');
});

window.addEventListener('scroll', function (e){
    check_feed_position();
});

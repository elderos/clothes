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


function refresh_score(data, score){
    const final_score = data.likes + (data.likes - data.votes);
    score.innerHTML = final_score > 0 ? '+' + final_score : final_score; 
}


function change_like_status(data, like_btn, score_wrapper, dislike_btn, vote){
    $.get(
        'vote?pairid=' + data.pair_id + '&vote=' + vote,
        null,
        function(answer_data, status, request){
            like_btn.removeClass('feed-post__panel__pressed');
            dislike_btn.removeClass('feed-post__panel__pressed');
            if (answer_data.status == 'like'){
                like_btn.addClass('feed-post__panel__pressed');
            } else if (answer_data.status == 'dislike'){
                dislike_btn.addClass('feed-post__panel__pressed');
            }
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
    score.appendTo(score_wraper);
    
    const dislike_link = $('<a>', {
        class: 'feed-post__panel__link feed-post__panel__dislike'
    });
    dislike_link.appendTo(btn_container);
    

    score_wrapper.appendTo(btn_container);
    refresh_score(data, score[0]);

    const like_link = $('<a>', {
        class: 'feed-post__panel__link feed-post__panel__like'
    });
    like_link.appendTo(btn_container);

    dislike_link.click(function(){
        change_like_status(data, like_link, score, dislike_link, 'dislike');
    });
    like_link.click(function(){
        change_like_status(data, like_link, score, dislike_link, 'like');
    });


    return panel;
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

    const panel = create_panel(data);
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

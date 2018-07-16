const FEED_PAGE_SIZE = 10;
var feed_offset = FEED_PAGE_SIZE;

function save(event){
    if (event == undefined) {
        return;
    }
    let e = $(event)
    let pid = e.parent().parent().parent().parent().attr('id')
    let post_id = pid.split(/_/)[1]
    $.get(
        'save',
        {'post_id':  post_id},
        function(data, status, request){
            e.parent().replaceWith(data);
        },
        'html'
    )

}

function send_vote(event){
    if (event == undefined) {
        return;
    }
    let e = $(event)
    let pid = e.parent().parent().parent().parent().attr('id')
    let post_id = pid.split(/_/)[1]
    let vote = e.hasClass('like') ? 'like' : 'dislike'
    $.get(
        'vote',
        {'post_id':  post_id, 'vote': vote},
        function(data, status, request){
            e.parent().replaceWith(data);
        },
        'html'
    )
}

function get_name(e) {
    if (e.id) {
        return e.id.split('-')[1];
    } else {
        return e.attr('id').split('-')[1];
    }
}

function append_feed_on_bottom(){
    return;
    let feed = $('#tabs > li.active');
    if (!feed[0]) {
        return 0;
    }
    let name = get_name(feed[0]);
    let rect = feed[0].getBoundingClientRect();
    let window_bottom = $(window).scrollTop() + $(window).height();
    if (rect.height - window_bottom < 250) {
        $.get(
            'fetch-feed/' + name,
            {'count': FEED_PAGE_SIZE, 'position': feed_offset},
            function(data, status, req) {
                $(data).appendTo(feed)
            },
            'html'
        );
        feed_offset += FEED_PAGE_SIZE

    }
}

function activate_tab(name){
    $("#tabs li").removeClass("active");
    $("#tabs-" + name + "-btn").addClass("active");
    $("#tabs-content > div").hide();
    $("#tabs-" + name + "-content").show();
}


window.addEventListener('load', function () {
    $('#tabs-filter-content').hide()
    tab = $('#tabs > li').first()
    activate_tab(get_name(tab))

    $('#tabs li').click(function(e) {
        name = get_name(this)
        if (name == 'filter') {
            $('#tabs-filter-content').toggle()
        } else {
            activate_tab(name);
        }
    });
    append_feed_on_bottom();
    window.addEventListener('scroll', append_feed_on_bottom);

    window.fbAsyncInit = function() {
        FB.init({
          appId      : '144119693124237',
          cookie     : true,
          xfbml      : true,
          version    : '3.0'
        });

        FB.AppEvents.logPageView();
    };

    (function(d, s, id){
     var js, fjs = d.getElementsByTagName(s)[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement(s); js.id = id;
     js.src = "https://connect.facebook.net/en_US/sdk.js";
     fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
});

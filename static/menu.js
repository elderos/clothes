window.addEventListener('load', function () {
    $('#menu-icon-container').click( function () {
        const scroll_pos = window.scrollY;
        if (scroll_pos > 10){
            this.prev_scroll = scroll_pos;
            window.scrollTo(0, 0);
        } else {
            window.scrollTo(0, this.prev_scroll);
        }
    });
});
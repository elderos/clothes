window.addEventListener('load', function () {
    $('#menu li').click(function(e) {
        $(this).children('a').each(function(){
            window.location.href = this.href;
        });
    });
});

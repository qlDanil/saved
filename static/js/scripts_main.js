AOS.init({
    duration: 800,
    easing: 'slide',
    once: false
});

window.onload = function () {
    var params = window
        .location
        .search
        .replace('?', '')
        .split('&')
        .reduce(
            function (p, e) {
                var a = e.split('=');
                p[decodeURIComponent(a[0])] = decodeURIComponent(a[1]);
                return p;
            },
            {}
        );
    if (params.hasOwnProperty('hashtag')) {
        $('#hashtag-all').removeClass('active');
        hashtags = params['hashtag'].split(' ');
        var i;
        for (i = 0; i < hashtags.length; i++) {
            let selector = '[id = ' + hashtags[i] + ']';
            $(selector).addClass('active');
        }
    }
};

(function ($) {
    "use strict";
    $('#search-button').on('click', function () {
        var search = $('#search-input').val();
        document.location.href = "?search=" + encodeURI(search);
    });
    document.addEventListener('click', function (e) {
        if (document.getElementById('search-group').contains(e.target)) {
            $('#search-input').addClass('isFocus');
        } else {
            $('#search-input').removeClass('isFocus');
        }
    });
})(jQuery);

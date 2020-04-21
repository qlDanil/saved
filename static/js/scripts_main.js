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

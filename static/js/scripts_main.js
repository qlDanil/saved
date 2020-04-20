AOS.init({
    duration: 800,
    easing: 'slide',
    once: false
});
window.onload = function() {
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
    var selector = '[id = ' + params['hashtag'] + ']';
    $(selector).addClass('active');
};

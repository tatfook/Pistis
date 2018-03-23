//

$(document).ready(function() {
    $('.ui.form').form({
        fields: {
            query: {
                identifier: 'query',
                rules: [{
                    type: 'regExp',
                    value: /^\w+\/\w+$/i,
                    prompt: 'url incomplete, fill in sth like "user/site"'
                }]
            }
        }
    });

    $('i.button').click(function() {
        console.log('click me');

        if ($('.ui.form').form('is valid', 'query')) {
            path = $('input[name="query"]').val();
            host = "http://keepwork.com/";
            url = host + path;

            var query = {
                'url': url
            };

            l = window.location;
            base_url = l.protocol + '//' + l.host + l.pathname;
            var new_url = base_url + '?' + $.param(query);

            window.location = new_url;
        }
    });

    $('input[name="query"]').keypress(function (e) {
        if (e.which == 13) {
            $('i.button').click();
            return false;
        }
    });
});

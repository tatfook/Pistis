//

$(document).ready(function () {
    console.log('ready');


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
});

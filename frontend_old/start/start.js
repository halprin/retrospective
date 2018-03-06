function start_retro() {
    let retro_name = $('#retrospective_name').val();
    let user_name = $('#user_name').val();

    let request_body = JSON.stringify({
        'retroName': retro_name,
        'adminName': user_name
    })

    $.ajax('http://retrospective-dev.us-east-1.elasticbeanstalk.com/api/retro', {
        data: request_body,
        type: 'POST',
        contentType: 'application/json'
    })
    .done(function(json) {
        let retro_id = json.retroId;
        let user_token = json.token;

        window.history.pushState('View Retrospective', '', '../view/')

        $('html').load('../view/?retroId=' + retro_id + '&token=' + user_token);
    })
    .fail(function() {
        window.alert('suck, it failed')
    });
}

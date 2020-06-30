function clock(){
    var date = new Date(),
        hours = (date.getHours() < 10) ? '0' + date.getHours() : date.getHours(),
        minutes = (date.getMinutes() < 10) ? '0' + date.getMinutes() : date.getMinutes(),
        seconds = (date.getSeconds() < 10) ? '0' + date.getSeconds() : date.getSeconds();
    document.getElementById('clock').innerHTML = 'Время: ' + hours + ':' + minutes +
    ':' + seconds + ' Msk';
}
setInterval(clock, 1000);

$(document).ready(function() {
    // Add refresh button after field (this can be done in the template as well)
    // {#$('img.captcha').after(#}
    // {#        $('<a href="#void" class="captcha-refresh">Refresh</a>')#}
    // {#        );#}
 
    // Click-handler for the refresh-link
    $('.captcha-refresh').click(function(){
        var $form = $(this).parents('form');
        var url = location.protocol + "//" + window.location.hostname + ":"
                  + location.port + "/captcha/refresh/";
 
        // Make the AJAX-call
        $.getJSON(url, {}, function(json) {
            $form.find('input[name="captcha_0"]').val(json.key);
            $form.find('img.captcha').attr('src', json.image_url);
        });
 
        return false;
    });
});
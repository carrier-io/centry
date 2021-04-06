$(document).ready(function() {
    $('[data-toggle="popover"]').popover({
        sanitizeFn: function(content) {return content}
    });
});

$('#severity_filter').click(function() {
    if ($(this).is(':checked')){
        $('#severity_filters').show();
    } else {
        $('#severity_filters').hide();
    }
})
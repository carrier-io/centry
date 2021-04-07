$('#use_another_jira').click(function(){
    if ($(this).is(':checked')){
        $('#another_jira').show();
    } else {
        $('#another_jira').hide();
    }
});

$('#epic_linkage_checkbox').click(function(){
    if ($(this).is(':checked')){
        $('#epic_linkage').show();
    } else {
        $('#epic_linkage').hide();
    }
});
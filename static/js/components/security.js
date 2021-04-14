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

function submitAppTest(event) {
    event.preventDefault();
    $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
    $("#submit").addClass("disabled");

    var data = new FormData();
    if ($('#repo').val() != '') {
        git_settings["repo"] = $('#repo').val()
        git_settings["repo_user"] = $('#repo_user').val()
        git_settings["repo_pass"] = $('#repo_pass').val()
        git_settings["repo_key"] = $('#repo_key').val()
        git_settings["repo_branch"] = $('#repo_branch').val()
        data.append('file', JSON.stringify({git: git_settings}));
    } else if ($('#file')[0].files[0] != undefined) {
        data.append('file', $('#file')[0].files[0], $('#file')[0].files[0].name);
    }
      data.append('funcname', $('#name').val());
      data.append('runtime', $('#runtime').val());
      data.append('region', $('#region').val());
      data.append('invoke_func', $('#handler').val());
      var env_vars = {}
      $("#runtimeConfig .row").slice(1,).each(function(_,item){
        var inp = $(item).find('input[type=text]')
        env_vars[inp[0].value] = inp[1].value
      })
      $("#envVars .row").slice(1,).each(function(_,item){
        var inp = $(item).find('input[type=text]')
        env_vars[inp[0].value] = inp[1].value
      })
      data.append('env_vars', JSON.stringify(env_vars));
      $.ajax(
        {
          url:`/api/v1/task/${getSelectedProjectId()}`,
          data: data,
          cache: false,
          contentType: false,
          processData: false,
          method: 'POST',
          success: function(data){
              $('#createTaskModal').modal('hide');
              $('#results-list').bootstrapTable('refresh');
          }
        }
      );
    }
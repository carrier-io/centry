$('#createTaskModal').on('hide.bs.modal', function(e) {
    clearTaskModal()
});

function createTask(event) {
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

function clearTaskModal(){
  $("#submit").html(`<span class="btn-inner--icon"><i class="fa fa-plus"></i></span>`);
  $("#submit").removeClass("disabled");
  $('#repo').val($('#repo')[0].defaultValue)
  $('#repo_user').val($('#repo_user')[0].defaultValue)
  $('#repo_pass').val($('#repo_pass')[0].defaultValue)
  $('#repo_key').val($('#repo_key')[0].defaultValue)
  $('#repo_branch').val($('#repo_branch')[0].defaultValue)
  $('#name').val($('#name')[0].defaultValue)
  $('#runtime').val($('#runtime option')[0].value)
  $('#runtime').selectpicker('refresh');
  $('#region').val($('#region option')[0].value)
  $('#region').selectpicker('refresh');
  $('#handler').val($('#handler')[0].defaultValue)
  $("#envVars .row").slice(1,).each(function(_, item){
    item.remove();
  })
  $('#runtimeConfig .row input[type="text"]').each(function(_, item){
    $(item).val(item.defaultValue)
  })
  if($('#runtimeConfig input[type="checkbox"]').prop('checked')) {
    $('#runtimeConfig input[type="checkbox"]').prop('checked', false);
    $('#runtimeConfig input[type="checkbox"]').trigger("change");
  }
}

$("#results-list").on('check.bs.table', function(e, row, element) {
    console.log(row);
})
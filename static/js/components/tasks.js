$('#createTaskModal').on('hide.bs.modal', function(e) {
    clearTaskModal()
});


function updateTask(event) {
  event.preventDefault();
  var data = new FormData();
  let task_id = $('#task-id').text()
  $("#update-task").html(`<span class="spinner-border spinner-border-sm"></span>`);
  $("#update-task").addClass("disabled");
  data.append('region', $('#exec-region').val());
  data.append('invoke_func', $('#handler_name').val());
  var env_vars = {}
  $("#runtimeConfig-config .row").slice(1,).each(function(_,item){
    var inp = $(item).find('input[type=text]')
    env_vars[inp[0].value] = inp[1].value
  })
  $("#envVars-config .row").slice(1,).each(function(_,item){
    var inp = $(item).find('input[type=text]')
    env_vars[inp[0].value] = inp[1].value
  })
  data.append('env_vars', JSON.stringify(env_vars));
  $.ajax(
    {
      url:`/api/v1/task/${getSelectedProjectId()}/${task_id}`,
      data: data,
      cache: false,
      contentType: false,
      processData: false,
      method: 'PUT',
      success: function(data){
          $("#update-task").html(`<span class="btn-inner--icon"><i class="fa fa-save"></i></span>`);
          $("#update-task").removeClass("disabled");
          $('#results-list').bootstrapTable('refresh');
      }
    }
  );
}


function runTask(ev) {
    $('label[for="event"]').parent().find('span').remove()
    var task_id = $("#task-id").text()
    var event_json = $("#event").val()
    try {
        JSON.parse(event_json)
    } catch (error) {
        $('label[for="event"]').append('<span class="badge badge-danger ml-3">Event should be in valid JSON format</span>');
        return;
    }
    if (event_json.length === 0) {
      event_json = "{}"
    }
    $.ajax(
      {
        url: `/api/v1/task/${getSelectedProjectId()}/${task_id}`,
        data: event_json,
        cache: false,
        contentType: "application/json",
        processData: false,
        method: 'POST',
        success: function(data){
          $('label[for="event"]').parent().parent().popover("hide");
        }
      }
    )
}

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

function deleteTask(){
    event.preventDefault();
    let task_id = $('#task-id').text()
    $.ajax(
    {
      url:`/api/v1/task/${getSelectedProjectId()}/${task_id}`,
      cache: false,
      contentType: false,
      processData: false,
      method: 'DELETE',
      success: function(data){
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
    $("#envVars-config .row").slice(1,).each(function(_, item){
        item.remove();
    })
    if($('#runtimeConfig-config input[type="checkbox"]').prop('checked')) {
        $('#runtimeConfig-config input[type="checkbox"]').prop('checked', false);
        $('#runtimeConfig-config input[type="checkbox"]').trigger("change");
      }
    $("#task-name").text(row.task_name);
    $("#task-id").text(row.task_id);
    $("#webhook").val(row.webhook);
    $("#runtime_name").val(row.runtime);
    $("#handler_name").val(row.task_handler);
    $('#exec-region').val(row.region);
    $('#exec-region').selectpicker('refresh');
    let envVars = JSON.parse(row.env_vars);
    Object.keys(envVars).forEach(function(key){
        if (["FUNCTION_TIMEOUT", "FUNCTION_MEMORY_SIZE"].indexOf(key) > -1) {
            $(`#${key}`).val(envVars[key])
        } else {
            addParam('envVars-config', key, envVars[key])
        }
    })
})

$("#results-list").on('load-success.bs.table', function(e, data, status, type) {
    $("#results-list").bootstrapTable('check', 0);
})


$(document).ready(function() {
    $("[data-toggle=popover]").popover({
        sanitizeFn: function(content) {return content}
    });
});

$('#createTestModal').on('hide.bs.modal', function(e) {
    createTestModal()
});

function createTestModal() {
    $('#repo').val($('#repo')[0].defaultValue)
    $('#repo_https').val($('#repo_https')[0].defaultValue)
    $('#repo_user').val($('#repo_user')[0].defaultValue)
    $('#repo_pass').val($('#repo_pass')[0].defaultValue)
    $('#repo_key').val($('#repo_key')[0].defaultValue)
    $('#repo_branch').val($('#repo_branch')[0].defaultValue)
    $('#local_file').val($('#local_file')[0].defaultValue)
    $('#repo_branch_https').val($('#repo_branch_https')[0].defaultValue)
    $('#testname').val($('#testname')[0].defaultValue)
    $('#parallel').val($('#parallel')[0].defaultValue)
    $('#entrypoint').val($('#entrypoint')[0].defaultValue)
    $('#runner').val($('#runner option')[0].value)
    $('#runner').selectpicker('refresh');
    $('#region').val($('#region option')[0].value)
    $('#region').selectpicker('refresh');
    $("#extCard .row").slice(1,).each(function(_, item){
      item.remove();
    })
    $("#scriptCard .row").slice(1,).each(function(_, item){
      item.remove();
    })
    $("#splitCSV .row").slice(1,).each(function(_, item){
      item.remove();
    })
}

function createTest() {
      $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#save").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#submit").addClass("disabled");
      $("#save").addClass("disabled");
//      var checked = []
      var params = [{}, {}, {}, {}]
      $("#scriptCard .row").slice(1,).each(function(_,item){
        var inp = $(item).find('input[type=text]')
        params[0][inp[0].value] = inp[1].value
      })
      $("#extCard .row").slice(1,).each(function(_,item){
        var inp = $(item).find('input[type=text]')
        params[3][inp[0].value] = inp[1].value
      })
//      $("input:checkbox:checked").each(function() {
//        if ($(this).attr("id") != "compile") {
//            checked.push($(this).attr("id"));
//        }
//      });
      var compile = $('#compile').is(":checked")
      event.preventDefault();

      var data = new FormData();
      git_settings = {}
      if ($('#repo').val() != '' || $('#repo_https').val() != '') {
        git_settings["repo"] = $('#repo').val() != '' ? $('#repo').val() : $('#repo_https').val()
        git_settings["repo_user"] = $('#repo_user').val()
        git_settings["repo_pass"] = $('#repo_pass').val()
        git_settings["repo_key"] = $('#repo_key').val()
        git_settings["repo_branch"] = $('#repo_branch').val() ? $('#repo_branch').val() : $('#repo_branch_https').val()
        data.append('git', JSON.stringify(git_settings));
      } else if ($('#file')[0].files[0] != undefined) {
        data.append('file', $('#file')[0].files[0], $('#file')[0].files[0].name);
      }  else if ($('#local_file').val() != '') {
        data.append('local_path', $('#local_file').val());
      }


      data.append('name', $('#testname').val());
      data.append('parallel', $('#parallel').val());
      data.append('region', $('#region').val());
      data.append('entrypoint', $('#entrypoint').val());
      data.append('runner', $('#runner').val());
      data.append('reporting', JSON.stringify({}));
      data.append('compile', compile);
      data.append('emails', $('#emails').val());
      data.append('params', JSON.stringify(params[0]));
      data.append('env_vars', JSON.stringify(params[1]));
      data.append('customization', JSON.stringify(params[2]));
      data.append('cc_env_vars', JSON.stringify(params[3]));

      $.ajax({
          url: `/api/v1/backend/${getSelectedProjectId()}`,
          data: data,
          cache: false,
          contentType: false,
          processData: false,
          method: 'POST',
          success: function(data){
              $("#submit").html(`<i class="fas fa-play"></i>`);
              $("#save").html(`<i class="fas fa-save"></i>`);
              $("#submit").removeClass("disabled");
              $("#save").addClass("disabled");
              $("#createTestModal").modal('hide');
              $("#tests-list").bootstrapTable('refresh');
          }
        }
      );
    }

function addCSVSplit(id, key="", is_header="") {
    $(`#${id}`).append(`<div class="row mt-2">
    <div class="col-6 ml-0">
        <input type="text" class="form-control" placeholder="File Path" value="${key}">
    </div>
    <div class="col pt-2">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" value="">
          <label class="form-check-label">file contains header</label>
        </div>
    </div>
    <div class="col-xs text-right">
        <button type="button" class="btn btn-nooutline-secondary mr-2" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
    </div>
</div>`)
}


function addDNSOverride(id, key="", value="") {
    $(`#${id}`).append(`<div class="row mt-2">
    <div class="col-6 ml-0">
        <input type="text" class="form-control" placeholder="hostname.company.com" value="${key}">
    </div>
    <div class="col">
        <input type="text" class="form-control" placeholder="0.0.0.0" value="${value}">
    </div>
    <div class="col-xs pt-1 text-right">
        <button type="button" class="btn btn-nooutline-secondary mr-2" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
    </div>
</div>`)
}

function lgFormatter(value, row, index) {
    if (row.job_type === "perfmeter") {
        return '<img src="/static/ico/jmeter.png" width="20">'
    } else if (row.job_type === "perfgun") {
        return '<img src="/static/ico/gatling.png" width="20">'
    } else {
        return value
    }
}

function actionFormatter(value, row, index) {
    return `<a class="mr-1 btn btn-sx" href="javascript:void(0)" onclick="showTestConfigModal(this, '${row.id}')" data-toggle="tooltip" data-placement="top" title="Run Test"><i class="fas fa-play"></i></a>
    <a class="mr-1 btn btn-sx" href="javascript:void(0)" onclick="editItem('${row.id}')" data-toggle="tooltip" data-placement="top" title="Edit Test"><i class="fas fa-cog"></i></a>
    <a class="mr-1 btn btn-sx" href="javascript:void(0)" onclick="copyToClipboard('${row.test_uid}')" data-toggle="tooltip" data-placement="top" title="Copy Test ID to clipboard"><i class="fas fa-cube"></i></a>
    <a class="btn btn-sx" href="javascript:void(0)" onclick="deleteTasks('${row.id}')" data-toggle="tooltip" data-placement="top" title="Delete Test"><i class="fa fa-trash-alt"></i></a>`
}

function copyToClipboard(text) {
    var dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
}


$("#tests-list").on("post-body.bs.table", function(data) {
    $('[data-toggle="tooltip"]').tooltip()
})

function cellStyle(value, row, index) {
    return {css: {"min-width": "165px"}}
}

function nameStyle(value, row, index) {
    return {css: {"max-width": "140px", "overflow": "hidden", "text-overflow": "ellipsis", "white-space": "nowrap"}}
}
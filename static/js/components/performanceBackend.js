$('#createTestModal').on('hide.bs.modal', function(e) {
    createTestModal()
});

$('#runTestModal').on('hide.bs.modal', function(e) {
    createTestModal()
});

function createTestModal() {
      console.log("Create modal")
//    $('#repo').val($('#repo')[0].defaultValue)
//    $('#repo_https').val($('#repo_https')[0].defaultValue)
//    $('#repo_user').val($('#repo_user')[0].defaultValue)
//    $('#repo_pass').val($('#repo_pass')[0].defaultValue)
//    $('#repo_key').val($('#repo_key')[0].defaultValue)
//    $('#repo_branch').val($('#repo_branch')[0].defaultValue)
//    $('#repo_branch_https').val($('#repo_branch_https')[0].defaultValue)
//    $('#test_name').val($('#test_name')[0].defaultValue)
//    $('#parallel').val($('#parallel')[0].defaultValue)
//    $('#entrypoint').val($('#entrypoint')[0].defaultValue)
//    $('#runner').val($('#runner option')[0].value)
//    $('#runner').selectpicker('refresh');
//    $('#region').val($('#region option')[0].value)
//    $('#region').selectpicker('refresh');
//    $("#extCard .row").slice(1,).each(function(_, item){
//      item.remove();
//    })
//    $("#scriptCard .row").slice(1,).each(function(_, item){
//      item.remove();
//    })
//    $("#splitCSV .row").slice(1,).each(function(_, item){
//      item.remove();
//    })
}

function createTest() {
      $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#save").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#submit").addClass("disabled");
      $("#save").addClass("disabled");
//      var checked = []
      var params = [[], {}, {}, {}]
//      $("#scriptCard .row").slice(1,).each(function(_,item){
//        var inp = $(item).find('input[type=text]')
//        params[0][inp[0].value] = inp[1].value
//      })
      params[0].push({"name": "test_name", "default": $('#test_name').val(), "description": "Name of the test", "type": "", "action": ""})
      params[0].push({"name": "env_type", "default": $('#test_env').val(), "description": "Env type (tag for filtering)", "type": "", "action": ""})
      params[0].push({"name": "test_type", "default": $('#test_type').val(), "description": "Test type (tag for filtering)", "type": "", "action": ""})
      $("#params_list").bootstrapTable('getData').forEach((param) => {
          params[0].push(param)
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


      data.append('name', $('#test_name').val());
      // TODO add in test planner UI
      //data.append('parallel', $('#parallel').val());
      data.append('parallel', 1);
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
    $(`#${id}`).append(`<div class="d-flex flex-row">
    <div class="flex-fill">
        <input type="text" class="form-control form-control-alternative" placeholder="File Path" value="${key}">
    </div>
    <div class="flex-fill m-auto pl-3">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" value="">
          <label class="form-check-label">Ignore first line</label>
        </div>
    </div>
    <div class="m-auto">
        <button type="button" class="btn btn-32 btn-action" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
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

function backendLgFormatter(value, row, index) {
    if (row.job_type === "perfmeter") {
        return '<img src="/static/vendor/design-system/assets/ico/jmeter.png" width="20">'
    } else if (row.job_type === "perfgun") {
        return '<img src="/static/vendor/design-system/assets/ico/gatling.png" width="20">'
    } else {
        return value
    }
}

function createLinkToTest(value, row, index) {
    return '<a href="/report/backend?report_id=' + row['id'] + '">' + value + '</a>'
}

function backendTestActionFormatter(value, row, index) {
    return `
        <div class="d-flex justify-content-end">
            <button type="button" class="btn btn-16 btn-action run" onclick="runTestModal('${row.id}')" data-toggle="tooltip" data-placement="top" title="Run Test"><i class="fas fa-play"></i></button>
            <div class="dropdown action-menu">
                <button type="button" class="btn btn-16 btn-action" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
                <div class="dropdown-menu bulkActions" aria-labelledby="bulkActionsBtn">
                    <a class="dropdown-item submenu" href="#"><i class="fas fa-share-alt fa-secondary fa-xs"></i> Integrate with</a>
                    <div class="dropdown-menu">
                        <a class="dropdown-item" href="#" onclick="console.log('Docker command')">Docker command</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Jenkins stage')">Jenkins stage</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Azure DevOps yaml')">Azure DevOps yaml</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Test UID')">Test UID</a>
                    </div>
                    <a class="dropdown-item settings" href="#"><i class="fas fa-cog fa-secondary fa-xs"></i> Settings</a>
                    <a class="dropdown-item trash" href="#"><i class="fas fa-trash-alt fa-secondary fa-xs"></i> Delete</a>
                </div>
            </div>
        </div>
        `
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

function runTestModal(test_id) {
    $("#runTestModal").modal('show');
    var test_data = $('#tests-list').bootstrapTable('getRowByUniqueId', test_id);
    console.log(test_data);
    $('#runner_test_params').bootstrapTable('removeAll')
    test_data.params.forEach((param) => {
        console.log(param)
        $('#runner_test_params').bootstrapTable('append', param)
    })
    $('#run_test').removeAttr('onclick');
    $('#run_test').attr('onClick', `runTest("${test_data.test_uid}")`);
    // TODO set region and load generators
    $('#runTest_region').val(test_data.region)
    $('#runTest_parallel').val(test_data.parallel)
}

function runTest(test_id) {
        console.log(`going to run test ${test_id}`)
        var params = []
        $("#runner_test_params").bootstrapTable('getData').forEach((param) => {
          params.push(param)
        })
        $("#nav-test-params .test_param").each(function() {
           if ($(this).children()[0].innerText !== "" && $(this).children()[1].value !== "") {
                params[$(this).children()[0].innerText] = $(this).children()[1].value;
           }
        });
        var env_vars = {}
        $("#nav-runner-env-vars .env_vars").each(function() {
           if ($(this).children()[0].innerText !== "" && $(this).children()[1].value !== "") {
                env_vars[$(this).children()[0].innerText] = $(this).children()[1].value;
           }
        });
        var cc_env_vars = {}
        $("#nav-cc-env-vars .cc_env_vars").each(function() {
           if ($(this).children()[0].innerText !== "" && $(this).children()[1].value !== "") {
                cc_env_vars[$(this).children()[0].innerText] = $(this).children()[1].value;
           }
        });
        var data = {
            'params': JSON.stringify(params),
            'env_vars': JSON.stringify(env_vars),
            'cc_env_vars': JSON.stringify(cc_env_vars),
            'parallel': $('#runTest_parallel').val(),
            'region': $('#runTest_region').val()
        }
        $.ajax({
            url: `/api/v1/tests/${getSelectedProjectId()}/backend/${test_id}`,
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: 'POST',
            success: function (result) {
                $("#runTestModal").modal('hide');
            }
        });
    }
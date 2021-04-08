function createTest() {
      $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#submit").addClass("disabled");
      $("#save").addClass("disabled");
      var checked = []
      var params = get_script_paras();
      $("input:checkbox:checked").each(function() {
        if ($(this).attr("id") != "compile") {
            checked.push($(this).attr("id"));
        }
      });
      var compile = $('#compile').is(":checked")
      var project_id = $("#selected-project-id").text();
      event.preventDefault();

      var data = new FormData();
      git_settings = {}
      if ($('#repo').val() != '') {
        git_settings["repo"] = $('#repo').val()
        git_settings["repo_user"] = $('#repo_user').val()
        git_settings["repo_pass"] = $('#repo_pass').val()
        git_settings["repo_key"] = $('#repo_key').val()
        git_settings["repo_branch"] = $('#repo_branch').val()
        data.append('git', JSON.stringify(git_settings));
      } else if ($('#file')[0].files[0] != undefined) {
        data.append('file', $('#file')[0].files[0], $('#file')[0].files[0].name);
      }

      data.append('name', $('#testname').val());
      data.append('parallel', $('#parallel').val());
      data.append('region', $('#region').val());
      data.append('entrypoint', $('#entrypoint').val());
      data.append('runner', $('#runner').val());
      data.append('reporter', checked);
      data.append('compile', compile);
      data.append('emails', $('#emails').val());
      data.append('params', JSON.stringify(params[0]));
      data.append('env_vars', JSON.stringify(params[1]));
      data.append('customization', JSON.stringify(params[2]));
      data.append('cc_env_vars', JSON.stringify(params[3]));

      $.ajax({
          url: `/api/v1/tests/${project_id}/backend`,
          data: data,
          cache: false,
          contentType: false,
          processData: false,
          method: 'POST',
          success: function(data){
            window.location.href = "/tests?type=backend";
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
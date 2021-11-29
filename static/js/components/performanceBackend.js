var presetsContext=document.getElementById("chart-requests").getContext("2d");
var analyticsContext=document.getElementById("chart-analytics").getContext("2d");


//$('#createTestModal').on('hide.bs.modal', function(e) {
//    createTestModal()
//});

$('#runTestModal').on('hide.bs.modal', function(e) {
   console.log("Create run backend test modal")
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
      $("#backend_test_params").bootstrapTable('getData').forEach((param) => {
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
      data.append('parallel', $('#backend_parallel').val());
      data.append('region', $('#backend_region option:selected').text());
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
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('module', 'Result');
    searchParams.set('page', 'list');
    searchParams.set('project_id', getSelectedProjectId());
    searchParams.set('result_test_id', row.id);
    searchParams.set('test_id', row.test_uid);
    return `<a class="test form-control-label" href="?${searchParams.toString()}" role="button">${row.name}</a>`
}

function backendTestActionFormatter(value, row, index) {
    return `
    <div class="d-flex justify-content-end">
        <button type="button" class="btn btn-24 btn-action" onclick="runTestModal('${row.id}')" data-toggle="tooltip" data-placement="top" title="Run Test"><i class="fas fa-play"></i></button>
        <button type="button" class="btn btn-24 btn-action"><i class="fas fa-cog"></i></button>
        <button type="button" class="btn btn-24 btn-action"><i class="fas fa-share-alt"></i></button>
        <button type="button" class="btn btn-24 btn-action"><i class="fas fa-trash-alt"></i></button>
    </div>
    `
}

function reportsStatusFormatter(value, row, index) {
    switch (value.toLowerCase()) {
        case 'canceled':
            return `<div style="color: var(--gray)">${value} <i class="fas fa-times-circle"></i></div>`
        case 'finished':
            return `<div style="color: var(--info)">${value} <i class="fas fa-check-circle"></i></div>`
        case 'in progress':
            return `<div style="color: var(--basic)">${value} <i class="fas fa-spinner fa-spin fa-secondary"></i></div>`
        default:
            return value
    }
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
    $('#runner_region').val(test_data.region)
    $('#runner_parallel').val(test_data.parallel)
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
                $("#results-list").bootstrapTable('refresh')
            }
        });
    }


function setParams(){
    build_id = document.querySelector("[property~=build_id][content]").content;
    lg_type = document.querySelector("[property~=lg_type][content]").content;
    test_name = document.querySelector("[property~=test_name][content]").content;
    environment = document.querySelector("[property~=environment][content]").content;
//    samplerType = $("#sampler").val().toUpperCase();
    // TODO set correct samplerType and statusType
    samplerType = "REQUEST"
   // statusType = $("#status").val().toLowerCase();
    statusType = "ok"
    aggregator = "auto";
}


function fillSummaryTable(){
    console.log("fillSummaryTable")
    $.get(
    '/api/v1/chart/requests/table',
    {
        build_id: build_id,
        test_name: test_name,
        lg_type: lg_type,
        sampler: samplerType,
        status: statusType,
        start_time: $("#start_time").html(),
        end_time: $("#end_time").html(),
        // TODO set correct low_value and high_value
        //low_value: $("#input-slider-range-value-low").html(),
        //high_value: $("#input-slider-range-value-high").html()
        low_value: 0,
        high_value: 100
    },
    function( data ) {
        console.log(data)
        data.forEach((item) => {
            console.log(item)
            $('#summary_table').bootstrapTable('append', item)
        })
    });
}

function loadRequestData(url, y_label) {
    if ( ! $("#preset").is(":visible") ) {
        $("#preset").show();
        $("#analytics").hide();
        if(analyticsLine!=null){
            analyticsLine.destroy();
        }
    }
//    if ($("#end_time").html() != "") {
//        $("#PP").hide();
//    }
    $.get(
      url,
      {
        build_id: build_id,
        test_name: test_name,
        lg_type: lg_type,
        sampler: samplerType,
        aggregator: aggregator,
        status: statusType,
        start_time: $("#start_time").html(),
        end_time: $("#end_time").html(),
        // TODO add time picker
//        low_value: $("#input-slider-range-value-low").html(),
//        high_value: $("#input-slider-range-value-high").html()
        low_value: 0,
        high_value: 100
      }, function( data ) {
        lineChartData = data;
        if(window.presetLine!=null){
            window.presetLine.destroy();
        }
        drawCanvas(y_label);
        document.getElementById('chartjs-custom-legend').innerHTML = window.presetLine.generateLegend();
      }
     );
}

function switchAggregator() {
    aggregator = $("#aggregator").val();
    console.log(aggregator)
    resizeChart();
}

function drawCanvas(y_label) {
    window.presetLine = Chart.Line(presetsContext, {
        data: lineChartData,
        options: {
            responsive: true,
            hoverMode: 'index',
            stacked: false,
            legend: {
                display: false,
                position: 'right',
                labels: {
                    fontSize: 10,
                    usePointStyle: false,
                    filter: function(legendItem, data) {
                        return legendItem.text != "Active Users";
                    }
                }
            },
            title:{
                display: false,
            },
            scales: {
                yAxes: [{
                    type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: "left",
                    scaleLabel: {
                        display: true,
                        labelString: y_label
                    },
                    id: "response_time",
                }, {
                    type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: "right",
                    scaleLabel: {
                        display: true,
                        labelString: "Active users"
                    },
                    id: "active_users",
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }],
            }
        }
    });
}

function fillErrorTable() {
    console.log("fillErrorTable")
    var start_time = $("#start_time").html()
    var end_time = $("#end_time").html()
    //var low_value = $("#input-slider-range-value-low").html()
    //var high_value = $("#input-slider-range-value-high").html()
    // TODO add time picker
    var low_value = 0
    var high_value = 100
    test_name = document.querySelector("[property~=test_name][content]").content;
    $('#errors').bootstrapTable('refreshOptions', {url: `/api/v1/chart/errors/table?test_name=${test_name}&start_time=${start_time}&end_time=${end_time}&low_value=${low_value}&high_value=${high_value}`})
}

function resizeChart() {
    if ( $("#analytics").is(":visible") ){
        analyticsData = null;
        analyticsLine.destroy();
        analyticsCanvas();
        recalculateAnalytics();
    }
    ["RT", "AR", "HT", "AN"].forEach( item => {
        if ($(`#${item}`).hasClass( "active" )) {
            $(`#${item}`).trigger( "click" );
        }
    });
    fillTable();
    fillErrorTable();
}



function detailFormatter(index, row) {
    var html = []
    html.push('<p><b>Method:</b> ' + row['Method'] + '</p>')
    html.push('<p><b>Request Params:</b> ' + row['Request params'] + '</p>')
    html.push('<p><b>Headers:</b> ' + row['Headers'] + '</p>')
    html.push('<p><b>Response body:</b></p>')
    html.push('<textarea disabled style="width: 100%">'+row['Response body']+'</textarea>')
    return html.join('')
}

function showConfig() {
    //TODO
    console.log("show test config")
}

function rerunTest() {
    //TODO
    console.log("rerun test with the same config")
}

function compareWithBaseline() {
    //TODO
    console.log("compare current report with baseline")
}

function setBaseline() {
    //TODO
    console.log("set current report as baseline")
}

function setThresholds() {
    //TODO
    console.log("set current report results as threshold")
}

function downloadReport() {
    //TODO
    console.log("download test report")
}

function shareTestReport() {
    //TODO
    console.log("share test report")
}
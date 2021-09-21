var scanners_cards = {};
var edit_test = false;


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

$('#createApplicationTest').on('hide.bs.modal', function(e) {
    edit_test = false;
    $("#submit").html(`<i class="fas fa-play"></i>`);
    $("#save").html(`<i class="fas fa-save"></i>`);
    $("#submit").removeClass("disabled");
    $("#save").removeClass("disabled");
    cleanAppTestModal()
});

function cleanAppTestModal() {
    $("#testname").val($("#testname")[0].defaultValue)
    $("#test_env").val($("#test_env")[0].defaultValue)
    $('#url_to_scan .row').slice(1,).each(function(_, item) {
        item.remove()
    })
    $("#scanURL").val($("#scanURL")[0].defaultValue)
    $('#exclusions .row').slice(1,).each(function(_, item) {
        item.remove()
    })
    $("#scanner_pool .row").slice(1,).each(function(_, item){
      item.remove();
    })
    var uncheck_flags = document.getElementsByTagName('input');
    for(var i=0;i<uncheck_flags.length;i++)
    {
        if(uncheck_flags[i].type=='checkbox' || uncheck_flags[i].type=='radio') {  // uncheck all checkboxes and radio buttons
            uncheck_flags[i].checked=false;
        }
    }
    $("#severity").selectpicker('val', "Info")
//    $("#qualys_checkbox").prop("checked", false)
}

function test_name_button(value, row, index) {
    const projectId = localStorage.getItem(selectedProjectLocalStorageKey);
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('module', 'Result');
    searchParams.set('page', 'list');
    searchParams.set('project_id', projectId);
    searchParams.set('result_test_id', row.id);
    searchParams.set('test_id', row.test_id);
    return `<a class="test form-control-label" href="?${searchParams.toString()}" role="button">${row.name}</a>`
}

var click_name = {
    "click .test": function(e, value, row, index) {
        alert("Now it's just an alert.. It will be modal window for canceling test soon")
    }
}

const badgeClasses = {
    'badge-dark': 0,
    'badge-light': 0,
    'badge-info': 0,
    'badge-warning': 0,
    'badge-danger': 0,
    'badge-success': 0,
    'badge-secondary': 0,
    'badge-primary': 0,
}

let tagBadgeMapping = {}

const getTagBadge = tag => {
    const tagLower = tag.toLowerCase()
    if (tagBadgeMapping[tagLower] === undefined) {
        const leastChosenClassName = Object.keys(badgeClasses).reduce(
            (className, current, index, item) =>
                badgeClasses[className] < badgeClasses[current] ? className : current
        )
        tagBadgeMapping[tagLower] = leastChosenClassName
        badgeClasses[leastChosenClassName]++
    }
    return tagBadgeMapping[tagLower]
}

function reportsTagFormatter(value, row, index) {
    const result = value?.map(item => {
        return `<span class="badge badge-pill ${getTagBadge(item)}">${item}</span>`
    })
    return result?.join(' ')
}

function reportsStatusFormatter(value, row, index) {
    switch (value.toLowerCase()) {
        case 'error':
        case 'failed':
            return `<div style="color: var(--red)">${value} <i class="fas fa-exclamation-circle error"></i></div>`
        case 'stopped':
            return `<div style="color: var(--yellow)">${value} <i class="fas fa-exclamation-triangle"></i></div>`
        case 'aborted':
            return `<div style="color: var(--gray)">${value} <i class="fas fa-times-circle"></i></div>`
        case 'finished':
            return `<div style="color: var(--info)">${value} <i class="fas fa-check-circle"></i></div>`
        case 'passed':
            return `<div style="color: var(--green)">${value} <i class="fas fa-check-circle"></i></div>`
        case 'pending...':
            return `<div style="color: var(--basic)">${value} <i class="fas fa-spinner fa-spin fa-secondary"></i></div>`
        default:
            return value
    }
}

function testActions(value, row, index) {
    return `
        <div class="d-flex justify-content-end">
            <button type="button" class="btn btn-16 btn-action"><i class="fas fa-play"></i></button>
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
                        <a class="dropdown-item" href="#" onclick="console.log('Settings')"><i class="fas fa-cog fa-secondary fa-xs"></i> Settings</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Delete')"><i class="fas fa-trash-alt fa-secondary fa-xs"></i> Delete</a>
                </div>
            </div>
        </div>
        `
}


function fillCardSettings(card_name, data) {
    if (card_name === "qualys"){
        $('#qualys_profile_id').val(data["qualys_profile_id"]);
        $('#qualys_template_id').val(data["qualys_template_id"]);

        if (data["scanner_type"] == "internal"){
            $("#QualysScannerType2").prop("checked",true);
        }
        else {
            $("#QualysScannerType1").prop("checked", true);
        }

        compareLength(data["scanner_pool"], "#scanner_pool")

        for (var indx=0; indx < data["scanner_pool"].length; indx++) {
            $($("#scanner_pool .row").slice(1, ).find('input[type=text]')[indx]).val(data["scanner_pool"][indx])
        }

    }
}

function compareLength(array, block_name){
    var list_ids = ["#exclusions", "#scanner_pool"]  // list of (blocks)IDs where we need to exclude first .row
    if (list_ids.find((i) => i === block_name) === block_name) {
        var block_length = $(block_name).length - 1
    }
    else {
        var block_length = $(block_name).length
    }

    if (array.length === block_length) {
        return true
    }
    else {
        block_name = block_name.slice(1,)
        for (var row_indx=0; row_indx<array.length-block_length; row_indx++){
            addNewURL(block_name)
        }
    }
}

var status_events = {
    "click .run": function (e, value, row, index) {
        $.ajax({
          url: `/api/v1/security/${getSelectedProjectId()}/dast/${row.id}`,
          cache: false,
          contentType: 'application/json',
          data: JSON.stringify({'test_name': row.name}),
          processData: false,
          method: 'POST',
          success: function(data){
              $("#results-list").bootstrapTable('refresh');
          }
        }
      );
    },

    "click .settings": function (e, value, row, index) {
        edit_test = row['test_uid'];
        $("#createApplicationTest").modal('show');

//        Fill main data
        $("#testname").val(row.name)
        $("#test_env").val(row["test_environment"])

        compareLength(row["urls_to_scan"], "#url_to_scan")
        compareLength(row["urls_exclusions"], "#exclusions")

        for (var indx=0; indx < row["urls_to_scan"].length; indx++) {
            $($("#url_to_scan .row").find('input[type=text]')[indx]).val(row["urls_to_scan"][indx])
        }
        for (var indx=0; indx < row["urls_exclusions"].length; indx++) {
            $($("#exclusions .row").find('input[type=text]')[indx]).val(row["urls_exclusions"][indx])
        }
//        Fill scanners data 'scanners_cards'
        $.each(row["scanners_cards"], function (key, value) {
            $("#"+`${key}_checkbox`).prop("checked", true)
            fillCardSettings(key, row["scanners_cards"][key])
        })
//        Fill processing data
        $("#severity").selectpicker('val', row["processing"]["minimal_security_filter"])
    },

    "click .integrations": function (e, value, row, index) {
        alert('You click INTEGRATIONS action')
//        TODO: write this method
    },

    "click .trash": function (e, value, row, index) {
        $.ajax({
          url: `/api/v1/security/${getSelectedProjectId()}/dast` + '?' + $.param({"id[]": row.id}),
          method: 'DELETE',
          success: function(data){
              $("#tests-list").bootstrapTable('refresh');
          }
        }
      );
    }
}

function getScannersData(){
    scannersContainer = document.getElementById("scannersCardsContainer");
    cards = scannersContainer.getElementsByClassName("card");

    for (i = 0; i < cards.length; i++) {
        scanner_id = cards[i].id
        window[scanner_id]();
    }
}

function saveTest(data) {
    if (edit_test) {
        $.ajax({
          url: `/api/v1/security/${getSelectedProjectId()}/dast/${edit_test}`,
          data: data,
          cache: false,
          contentType: false,
          processData: false,
          method: 'PUT',
          success: function(data){
              $("#submit").html(`<i class="fas fa-play"></i>`);
              $("#save").html(`<i class="fas fa-save"></i>`);
              $("#submit").removeClass("disabled");
              $("#save").addClass("disabled");
              $("#createApplicationTest").modal('hide');
              $("#tests-list").bootstrapTable('refresh');
              $("#results-list").bootstrapTable('refresh');
          }
        });
    } else {
        $.ajax({
          url: `/api/v1/security/${getSelectedProjectId()}/dast`,
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
              $("#createApplicationTest").modal('hide');
              $("#tests-list").bootstrapTable('refresh');
              $("#results-list").bootstrapTable('refresh');
          }
        }
      );
    }
    edit_test = false;
}

function submitAppTest(run_test=false) {
      $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#save").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#submit").addClass("disabled");
      $("#save").addClass("disabled");

//      Main variables
      var urls_params = [[], []]
      var run_test = run_test
      var processing_cards = {"minimal_security_filter": null}

//      Urls to scan and extensions
      $("#url_to_scan .row").each(function(_, item) {
        var url_ = $(item).find('input[type=text]')
        urls_params[0].push(url_.val())
      })
      $("#exclusions .row").slice(1,).each(function(_, item) {
        var url_ = $(item).find('input[type=text]')
        urls_params[1].push(url_.val())
      })

//      --Scanner's cards--
      getScannersData();

//      --Processing's cards--
//      Min security filter
      processing_cards["minimal_security_filter"] = $("#severity").val()

      var data = new FormData();

      data.append('name', $('#testname').val());
      // data.append('project_name', document.getElementById("selected-project").textContent);
      data.append('project_name', getProjectNameFromId(getSelectedProjectId()));
      data.append('test_env', $("#test_env").val());
      data.append('urls_to_scan', JSON.stringify(urls_params[0]));
      data.append('urls_exclusions', JSON.stringify(urls_params[1]));
      data.append('scanners_cards', JSON.stringify(scanners_cards));
      data.append('reporting', JSON.stringify({}));
      data.append('processing', JSON.stringify(processing_cards));
      data.append('run_test', run_test)

//      TODO: write reporting cards parser
//      var reporting_cards = reportingCards()
//      data.append("reporting_cards", JSON.stringify(reporting_cards))

       saveTest(data)

//      $.ajax({
//          url: `/api/v1/security/${getSelectedProjectId()}/dast`,
//          data: data,
//          cache: false,
//          contentType: false,
//          processData: false,
//          method: 'POST',
//          success: function(data){
//              $("#submit").html(`<i class="fas fa-play"></i>`);
//              $("#save").html(`<i class="fas fa-save"></i>`);
//              $("#submit").removeClass("disabled");
//              $("#save").addClass("disabled");
//              $("#createApplicationTest").modal('hide');
//              $("#tests-list").bootstrapTable('refresh');
//              $("#results-list").bootstrapTable('refresh');
//          }
//        }
//      );
    }
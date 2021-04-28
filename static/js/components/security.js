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

function actions_buttons(value, row, index) {
    return [
        '<button id="run_test" class="run btn btn-secondary btn-sm"><span class="btn-inner--icon"><i class="fa fa-play fa-lg"></i></span></button>',
        '<button id="test_settings" class="settings btn btn-secondary btn-sm"><span class="btn-inner--icon"><i class="fa fa-cog fa-lg"></i></span></button>',
        '<button id="integrations" class="integrations btn btn-secondary btn-sm"><span class="btn-inner--icon"><i class="fa fa-share-alt-square fa-lg"></i></span></button>',
        '<button id="delete" class="trash btn btn-secondary btn-sm"><span class="btn-inner--icon"><i class="fa fa-trash fa-lg"></i></span></button>'
    ].join(' ')
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
        $("#createApplicationTest").modal('show');

//        Fill main data
        $("#testname").val(row.name)

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
            console.log(row["scanners_cards"])
            fillCardSettings(key, row["scanners_cards"][key])
        })



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


function submitAppTest(run_test=false) {
      $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#save").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#submit").addClass("disabled");
      $("#save").addClass("disabled");

//      Main variables
      var urls_params = [[], []]
      var scanners_cards = {qualys: {}}
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
//      Qualys
      if ($("#qualys_checkbox").prop("checked")){
        scanners_cards.qualys["qualys_profile_id"] = $("#qualys_profile_id").val()
        scanners_cards.qualys["qualys_template_id"] = $("#qualys_template_id").val()
        scanners_cards.qualys["scanner_type"] = $("input[name=scanner_type]:checked", "#qualys_scanner_type").val()
        scanners_cards.qualys["scanner_pool"] = []

        $("#scanner_pool .row").slice(1,).each(function(_, item) {
            var scanner_pool = $(item).find('input[type=text]')
            scanners_cards.qualys["scanner_pool"].push(scanner_pool.val())
        })
      }

//      --Processing's cards--
//      Min security filter
      processing_cards["minimal_security_filter"] = $("#severity").val()

      var data = new FormData();

      data.append('name', $('#testname').val());
      data.append('project_name', document.getElementById("selected-project").textContent);
      data.append('test_env', $("#test_env").val());
      data.append('urls_to_scan', JSON.stringify(urls_params[0]));
      data.append('urls_exclusions', JSON.stringify(urls_params[1]));
      data.append('scanners_cards', JSON.stringify(scanners_cards));
      data.append('reporting', JSON.stringify({}));
      data.append('processing', JSON.stringify(processing_cards));
      data.append('run_test', run_test)

//      var reporting_cards = reportingCards()
//      data.append("reporting_cards", JSON.stringify(reporting_cards))

      for(var pair of data.entries()) {
           console.log(pair[0]+ '--> '+ pair[1]);
        }


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
          }
        }
      );
    }
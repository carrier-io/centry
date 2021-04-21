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

function submitAppTest(run_test=false) {
      $("#submit").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#save").html(`<span class="spinner-border spinner-border-sm"></span>`);
      $("#submit").addClass("disabled");
      $("#save").addClass("disabled");

//      Main variables
      var urls_params = [[], []]
      var scanners_cards = {qualys: {}}
      var run_test = run_test

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

      var data = new FormData();

      data.append('name', $('#testname').val());
      data.append('urls_to_scan', JSON.stringify(urls_params[0]));
      data.append('urls_exclusions', JSON.stringify(urls_params[1]));
      data.append('scanners_cards', JSON.stringify(scanners_cards));
      data.append('reporting', JSON.stringify({}));
      data.append('save_and_run', run_test)

//      var reporting_cards = reportingCards()
//      data.append("reporting_cards", JSON.stringify(reporting_cards))

//      for(var pair of data.entries()) {
//           console.log(pair[0]+ '--> '+ pair[1]);
//        }


      $.ajax({
          url: `/api/v1/security/${getSelectedProjectId()}`,
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
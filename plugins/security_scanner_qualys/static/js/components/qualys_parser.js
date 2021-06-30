
function scanner_qualysCard() {

//      Qualys
      if ($("#scanner_qualys_checkbox").prop("checked")){
        console.log("CHECKED")
        scanners_cards.qualys = {};
        scanners_cards.qualys["qualys_profile_id"] = $("#scanner_qualys_profile_id").val();
        scanners_cards.qualys["qualys_template_id"] = $("#scanner_qualys_template_id").val();
        scanners_cards.qualys["scanner_type"] = $("input[name=scanner_type]:checked", "#scanner_qualys_scanner_type").val();
        scanners_cards.qualys["scanner_pool"] = [];

        $("#scanner_scanner_pool .row").slice(1,).each(function(_, item) {
            var scanner_pool = $(item).find('input[type=text]');
            scanners_cards.qualys["scanner_pool"].push(scanner_pool.val());
        })
      }

}
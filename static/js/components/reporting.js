// $('#use_another_jira').click(function(){
//     if ($(this).is(':checked')){
//         $('#another_jira').show();
//     } else {
//         $('#another_jira').hide();
//     }
// });
//
// $('#epic_linkage_checkbox').click(function(){
//     if ($(this).is(':checked')){
//         $('#epic_linkage').show();
//     } else {
//         $('#epic_linkage').hide();
//     }
// });
//
// //      --Reporting cards--
// function reportingCards(){
//       var reporting_cards = {jira: {}}
//
// //      Jira
//       if ($("#jira_checkbox").prop("checked")){
//         reporting_cards.jira["jira_fields"] = []
//         reporting_cards.jira["priority_mapping"] = {}
//         reporting_cards.jira["limits"] = []
//         reporting_cards.jira["dynamic_fields"] = []
//         reporting_cards.jira["another_jira"] = {}
//
//
//         $("#jira_fields .row").each(function(_, item) {
//             var fields = $(item).find('input[type=text]')
//             reporting_cards.jira["jira_fields"].push(fields.val())
//           })
//
//         reporting_cards.jira["priority_mapping"]["priority_medium"] = $("#priority_medium").val()
//         reporting_cards.jira["priority_mapping"]["priority_high"] = $("#priority_high").val()
//         reporting_cards.jira["priority_mapping"]["priority_low"] = $("#priority_low").val()
//         reporting_cards.jira["priority_mapping"]["priority_info"] = $("#priority_info").val()
//         reporting_cards.jira["priority_mapping"]["priority_critical"] = $("#priority_critical").val()
//
//         reporting_cards.jira.limits.push($("#max_desc_size").val())
//         reporting_cards.jira.limits.push($("#max_comm_size").val())
//
//         $("#dynamic_fields .row").slice(1,).each(function(_, item) {
//             var fields = $(item).find('input[type=text]')
//             reporting_cards.jira["dynamic_fields"].push([fields[0].value, fields[1].value, fields[2].value])
//           })
//
//         if ($("#epic_linkage_checkbox").prop("checked")){
//             $("#epic_linkage_checkbox .row").each(function(_, item) {
//                 var epic_key = $(item).find('input[type=text]')
//                 reporting_cards.jira["epic_field_key"] = epic_key.val()
//               })
//         }
//
//         if ($("#use_another_jira").prop("checked")){
//             reporting_cards.jira["another_jira"]["url"] = $("#url_another_jira").val()
//             reporting_cards.jira["another_jira"]["creds"] = [$("#login_another_jira").val(), $("#password_another_jira").val()]
//         }
//
//         if ($("#reopen_jira").prop("checked")){
//             reporting_cards.jira["reopen"] = true
//         }
//
//       return reporting_cards;
//       }
//     }
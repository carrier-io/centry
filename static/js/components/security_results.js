// var page_params = new URLSearchParams(window.location.search);
//
// $(document).ready(function() {
//     updateRowAbove(page_params.get('result_test_id'));
// })
//
// var statuses_before = []
//
// function getTestsMainInfo() {
//     test_id = page_params.get('result_test_id');
//     project_id = page_params.get('project_id');
//     $.ajax({
//         url: `/api/v1/security/${project_id}/dast/${test_id}`,
//         cache: false,
//         contentType: false,
//         processData: false,
//         method: 'GET',
//         success: function(data){
// //            console.log(data);
//             $("#test_status").text(data['test_status']['status']);
//             $("#progressbar")[0].setAttribute("style", "width:" + data['test_status']['percentage'] + "%");
//             $("#test_status_description").text(data['test_status']['description']);
//             $("#first_started_date").text(data['start_date']);
//             statuses_before.push(data['test_status']);
//
//             if (data['test_status']['status'] == "Finished") {
//                 clearInterval(timerId);
//                 console.log("Test finished :)")
//                 console.log(statuses_before)
//                 if (statuses_before.length != 1) {
//                     $("#progressbar")[0].setAttribute("style", "width:100%");
//                     $("#progressbar").removeClass("progress-bar-striped active");
//                     $("#test_status").text("Finished");
//                     $("#processing-table").hide();
//                 } else {
//                     $("#progressbar-body").hide();
//                 }
//                 $("#findings-small-cards").show();
//                 $("#full-info-table").show();
//                 $("#stop-test").hide();
//                 $("#rerun-test").show();
//                 $("#config-test").show();
//                 $("#all_findings").show();
//                 // test_id = page_params.get('test_id')
//                 updateRowAbove(test_id);
//                 refreshTable(test_id);
//                 $("#all_artifacts").show();
//                 $("#all_logs").hide();
//                 return
//             }
//
//             if (data['test_status']['status'] == "Processing") {
//                 $("#progressbar").addClass("progress-bar-striped active");
//             }
//
//             $("#processing-table").show();
//             $("#progressbar-body").show();
//             $("#all_logs").show();
//           }
//         }
//       );
// }
//
//
// let timerId = setInterval(getTestsMainInfo, 1000)
//
//
// function rerunTest(){
// //TODO: write this method
//     console.log("Re-run button pressed")
// //    $.ajax({
// //          url: `/api/v1/security/${getSelectedProjectId()}/findings/2`,
// //          cache: false,
// //          contentType: false,
// //          processData: false,
// //          method: 'GET',
// //          success: function(data){
// //            console.log("sent");
// //          }
// //        }
// //      );
// }
//
// function showConfig() {
// //TODO: write this method
//     console.log("show config button pressed")
// }
//
// function stopTest(){
// //TODO: write this method
//     console.log("stop test button pressed")
// }
//
// function fillRowValues(data){
// //    update test name
//     $("#test_title").text(data['name']);
//
// //    update progressbar's text
//     $("#test_status").text(data['test_status']['status']);
//
// //    update cards in row
//     $("#critical_findings").text(data['critical']);
//     $("#high_findings").text(data["high"]);
//     $("#medium_findings").text(data["medium"]);
//     $("#low_findings").text(data["low"]);
//     $("#info_findings").text(data["info"]);
//
// //    update table values
//     $("#started_date").text(data['start_date']);
//     $("#test_scanners").text(data['scanners']);
//     $("#valid_values").text(data["valid"]);
// //    $("#test_env").text(data['test_environment']);
//     $("test_urls").text(data['urls_to_scan']);
//     $("#test_duration").text(`${data['duration']} S`);
//     $("#test_findings").text(data['findings']);
//     $("#fp_values").text(data["false_positive"]);
//     $("#ignored_values").text(data["ignored"]);
//     $("#ended_date").text(data["ended_date"]);
//     $("#test_tags").text(data['tags']);
// }
//
// function updateRowAbove(test_id) {
//     $.ajax({
//       url: `/api/v1/security/${getSelectedProjectId()}/dast/${test_id}`,
//       cache: false,
//       contentType: false,
//       processData: false,
//       method: 'GET',
//       success: function(response_data){
//         fillRowValues(response_data);
//       }
//     }
//   );
// }
//
// function refreshTable(test_id) {
//     $("#test-findings-list").bootstrapTable("refresh", {
//         url: `/api/v1/security/${getSelectedProjectId()}/findings/${test_id}`
//     });
// }
//
//
// function specialFilter(filter_value, test_id){
//     $("#test-findings-list").bootstrapTable(
//         "refresh",
//         {url: `/api/v1/security/${getSelectedProjectId()}/findings/${test_id}?type=${filter_value}`}
//     )
// }
//
// function detailFormatter(index, row){
//     var html = []
//     html.push('<div class="col ml-3"><div class="details_view"><p><b>Issue Details:</b></p> ' + row['details'] + '<br /></div></div>')
//     return html.join('')
// }
//
// function detailIconFormatter(value, row, index){
//     return [
//       '<a class="iconn btn btn-link btn-sm" href="javascript:void(0)"><i class="fas fa-chevron-down"></i></a>'
//     ].join('')
// }
//
// var detailIconEvents = {
//     'click .iconn': function (e, value, row, index) {
//         $(e.currentTarget).find('i').toggleClass('fa-chevron-down').toggleClass('fa-chevron-up')
//         $("#test-findings-list").bootstrapTable('toggleDetailView', index)
//     }
//   }
//
//
// function set_finding_severity(value, row, index) {
//     var available_statuses = ["Critical", "High", "Medium", "Low", "Info"]
//     var current_class = `severity_${row.severity}`.toLowerCase()
//     var upperName = `${row.severity}`.toUpperCase()
//
//     var result_block = [
//         `<a class="${current_class} nav-link dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false" style="width: 35%; border-radius: 0.3rem;">${upperName}</a>`,
//         '<div class="dropdown-menu">'
//         ]
//
//     available_statuses.forEach( function(item, i, available_statuses) {
//         var current_class = `severity_${item}`.toLowerCase()
//         var upperName = `${item}`.toUpperCase()
//         var html_text = `<a class="${current_class} dropdown-item" href="javascript:void(0)" onclick="setSeverityOrStatus('severity', ${row.id}, ${row['report_id']}, '${item}')" style="background-color: #ffffff">${upperName}</a>`
//         result_block.push(html_text)
//     })
//
//     result_block.push("</div>")
//     return result_block.join('')
// }
//
//
// function set_finding_status(value, row, index) {
//     var available_statuses = ["False Positive", "Not defined", "Valid", "Ignored"]
//     var changed_style_name = `${row.status}`.replace(/ /g, '_')
//     var current_class = `status_${changed_style_name}`.toLowerCase()
//
//     var result_block = [
//         `<a class="${current_class} nav-link dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false" style="width: 35%; border-radius: 0.3rem;">${row.status}</a>`,
//         '<div class="dropdown-menu">'
//         ]
//
//     available_statuses.forEach( function(item, i, available_statuses) {
//         var current_class = `status_${item}`.toLowerCase().replace(/ /g, '_')
//         var upperName = `${item}`.toUpperCase()
//         var html_text = `<a class="${current_class} dropdown-item" href="javascript:void(0)" onclick="setSeverityOrStatus('status', ${row.id}, ${row['report_id']}, '${item}')" style="background-color: #ffffff">${upperName}</a>`
//         result_block.push(html_text)
//     })
//
//     result_block.push("</div>")
//     return result_block.join('')
// }
//
//
// function setSeverityOrStatus(entry_type, row_id, report_id, item) {
//
//     var data = {
//         [entry_type]: item,
//         issues_id: [row_id]
//     }
//
//     $.ajax({
//         url: `/api/v1/security/${getSelectedProjectId()}/findings/${report_id}`,
//         type: "PUT",
//         contentType: 'application/json',
//         data: JSON.stringify(data),
//         success: function(response){
//             $("#test-findings-list").bootstrapTable('refresh');
//             updateRowAbove(`${report_id}`);
//         }
//     })
// }
//
// function bulkModify(type, value) {
//     var issues_list = []
//     $("#test-findings-list").bootstrapTable('getSelections').forEach(item => {
//         issues_list.push(item['id'])
//     })
//
//     applyModify(issues_list, value, type)
// }
//
//
// function applyModify(issues, value, type){
//
//     var report_id = page_params.get('test_id')
//     var data = {
//         "issues_id": issues,
//         [type]: value
//     }
//
//     $.ajax({
//         url: `/api/v1/security/${getSelectedProjectId()}/findings/${report_id}`,
//         type: "PUT",
//         contentType: 'application/json',
//         data: JSON.stringify(data),
//         success: function(response){
//             $("#test-findings-list").bootstrapTable('refresh');
//             updateRowAbove(`${report_id}`);
//         }
//     })
// }
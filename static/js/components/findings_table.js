const severityOptions = [
    {name: 'critical', className: 'colored-select-red'},
    {name: 'high', className: 'colored-select-orange'},
    {name: 'medium', className: 'colored-select-yellow'},
    {name: 'low', className: 'colored-select-green'},
    {name: 'info', className: 'colored-select-blue'},
]

const statusOptions = [
    {name: 'valid', className: 'colored-select-red'},
    {name: 'false positive', className: 'colored-select-blue'},
    {name: 'ignore', className: 'colored-select-darkblue'},
    {name: 'not defined', className: 'colored-select-notdefined'},
]

function tableSeverityButtonFormatter(value, row, index) {
    return tableColoredSelectFormatter(value, row, index, severityOptions)
}

function tableStatusButtonFormatter(value, row, index) {
    return tableColoredSelectFormatter(value, row, index, statusOptions)
}

const tableColoredSelectFormatter = (value, row, index, optionsList) => {
    console.log('value', value)
    console.log('row', row)
    console.log('index', index)
    const options = optionsList.map(item => `
        <option class="${item.className}" ${item.name === value ? 'selected' : ''}>${item.name}</option>
    `);
    const tmp = optionsList.find(item => item.name === value)
     tmp === undefined && options.push(
        `<option selected>${value}</option>`
    )
    return `<select class="selectpicker btn-colored-select" data-style="btn-colored">
                ${options.join('')}
            </select>`
}


page_params = new URLSearchParams(window.location.search);

$(document).ready(function () {
    // $('#all').trigger( "click" );
    renderTableCustom();
    filters();
})

function filters() {
    $("#errors").bootstrapTable('clearFilterControl');
    if ($(".filter-control input").css("visibility") === "visible") {
        $(".filter-control input").css("visibility", "hidden")
        $(".filter-control select").css("visibility", "hidden")
        $(".fht-cell").css("display", "none")
    } else {
        $(".filter-control input").css("visibility", "visible")
        $(".filter-control select").css("visibility", "visible")
        $(".fht-cell").css("display", "block")
    }
}

function renderTableCustom() {
    $('#errors').on('all.bs.table', function (e) {
      $('.selectpicker').selectpicker('render');
      initColoredSelect();
    })
    $("#errors").bootstrapTable('refresh', {
        url: `/api/v1/security/${page_params.get('project_id')}/findings/${page_params.get('test_id')}`,

    })

}

function statusFormatter(value, row, index) {
    if (row['false_positive'] == 1) {
        return '<button type="button" class="btn btn-ok btn-sm" disabled>false positive</button>'
    } else if (row['excluded_finding'] == 1) {
        return '<button type="button" class="btn btn-default btn-sm" disabled>Excluded</button>'
    } else {
        return '<button type="button" class="btn btn-warning btn-sm" disabled>valid</button>'
    }
}

function actionsFormatter(value, row, index) {
    var report_id = page_params.get("id");
    return `<div class="btn-group btn-group-sm" role="group" aria-label="Actions">
                    <button type="button" class="btn btn-danger" onclick="validFunding(${report_id}, ${row['id']})">Valid</button>
                    <button type="button" class="btn btn-warning" onclick="falsePositive(${report_id}, ${row['id']})">False Positive</button>
                    <button type="button" class="btn btn-default" onclick="ignoreIssue(${report_id}, ${row['id']})">Ignore</button>
                 </div>`

}

function bulkModify(action) {
    var issues_ids = []
    $("#errors").bootstrapTable('getSelections').forEach(item => {
        issues_ids.push(item["id"])
    })
    bulk_modify(issues_ids, action);
}

function bulk_modify(issues_id, action) {
    var report_id = page_params.get("id");
    var project_id = $("#selected-project-id").text();
    var url = `/api/v1/security/${project_id}/finding`;
    data = {
        id: report_id,
        action: action,
        issues_id: issues_id
    }
    $.ajax({
        url: url,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function (result) {
            window.location.reload();
        }
    });
}

function modify_issue(report_id, issue_id, action) {
    var project_id = $("#selected-project-id").text();
    var url = `/api/v1/security/${project_id}/finding`;
    data = {
        id: report_id,
        action: action,
        issue_id: issue_id
    }
    $.ajax({
        url: url,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function (result) {
            $("#errors").bootstrapTable('refresh');
        }
    });
}

function falsePositive(report_id, issue_id) {
    modify_issue(report_id, issue_id, "false_positive")
}

function validFunding(report_id, issue_id) {
    modify_issue(report_id, issue_id, "valid")
}

function ignoreIssue(report_id, issue_id) {
    modify_issue(report_id, issue_id, "excluded_finding")
}

function detailFormatter(index, row) {
    var html = []
    html.push('<p><b>Issue Details:</b></p> ' + row['details'] + '<br />')
    return html.join('')
}

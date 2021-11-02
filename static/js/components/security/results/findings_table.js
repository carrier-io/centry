page_params = new URLSearchParams(window.location.search);

let urlParamsFindings = '';
const getTableUrlFindings = () => `/api/v1/security/${page_params.get('project_id')}/findings/${page_params.get('result_test_id')}${urlParamsFindings}`

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
    {name: 'ignored', className: 'colored-select-darkblue'},
    {name: 'not defined', className: 'colored-select-notdefined'},
]


function tableSeverityButtonFormatter(value, row, index) {
    return tableColoredSelectFormatter(value, row, index, severityOptions, 'severity')
}

function tableStatusButtonFormatter(value, row, index) {
    return tableColoredSelectFormatter(value, row, index, statusOptions, 'status')
}


const compareValues = (value1, value2) => value1.toLowerCase() === value2.toLowerCase()


/*

$(document).ready(function () {
    renderTableCustom();
})


 function renderTableCustom() {
    $('#errors').on('all.bs.table', function (e) {
      $('.selectpicker').selectpicker('render');
      initColoredSelect();
    })
    $("#errors").bootstrapTable('refresh', {
        url: `/api/v1/security/${page_params.get('project_id')}/findings/${page_params.get('test_id')}`,
*/

const onSelectChange = (fieldName, value, issueHashes) => {
    const data = {
        [fieldName]: value,
        issue_hashes: issueHashes
    }
    fetch(getTableUrlFindings(), {
        method: 'PUT',
        body: JSON.stringify(data),
        headers: {'Content-Type': 'application/json'}
    }).then(response => {
        // console.log(response);
        renderTableFindings();
        $( document ).trigger( 'updateSummaryEvent' );
    })
}

const tableColoredSelectFormatter = (value, row, index, optionsList, fieldName) => {
    const options = optionsList.map(item => `
        <option 
            class="${item.className}" 
            ${compareValues(item.name, value) ? 'selected' : ''}
        >
            ${item.name}
        </option>
    `);
    const unexpectedValue = optionsList.find(item => compareValues(item.name, value))
    unexpectedValue === undefined && options.push(`<option selected>${value}</option>`)

    return `
        <select 
            class="selectpicker btn-colored-select" 
            data-style="btn-colored" 
            onchange="onSelectChange('${fieldName}', this.value, ['${row['issue_hash']}'])"
        >
            ${options.join('')}
        </select>
    `
}


function renderTableFindings() {
    $("#errors").bootstrapTable('refresh', {
        url: getTableUrlFindings(),
    })
}

const bulkModify = (dataType, value) => {
    const issueHashes = $('#errors').bootstrapTable('getSelections').map(item => item.issue_hash)
    if (issueHashes.length > 0) {
        // console.log('issues_ids', issueHashes);
        const data = {
            issue_hashes: issueHashes,
            [dataType]: value
        }
        fetch(getTableUrlFindings(), {
            method: 'PUT',
            body: JSON.stringify(data),
            headers: {'Content-Type': 'application/json'}
        }).then(response => {
            // console.log(response);
            renderTableFindings();
            $( document ).trigger( 'updateSummaryEvent' );
        })
    }
}


const statusFilter = value => {
    const valueMap = {
        all: '',
        valid: 'valid',
        'false positive': 'false_positive',
        ignored: 'ignored'
    }
    // console.log('Filter Selected', valueMap[value])
    // urlParamsFindings = value.toLowerCase() === 'all' ? '' : `/?status=${valueMap[value.toLowerCase()]}`;
    urlParamsFindings = `/?status=${valueMap[value.toLowerCase()]}`;
    // console.log('new url', getTableUrlFindings())
    renderTableFindings();
}

function findingsDetail(index, row) {
    return _findingsDetail(index, row)
}

const _findingsDetail = (index, row) => {
    return `
        <div class="col ml-3">
            <div class="details_view">
                <p><b>Issue Details:</b></p> ${row['details']} <br />
            </div>
        </div>
    `
}

$.when( $.ready ).then(function() {
    $('#errors').on('all.bs.table', function (e) {
        $('.selectpicker').selectpicker('render');
        initColoredSelect();
    })
    renderTableFindings();
});
page_params = page_params || new URLSearchParams(window.location.search);

const getTableUrlArtifacts = () => `/api/v1/artifact/security/${page_params.get('result_test_id')}`

$(document).ready(function () {
    renderTableArtifacts()
})

function renderTableArtifacts() {
    $("#artifacts").bootstrapTable('refresh', {
        url: getTableUrlArtifacts(),
    })
}

function artifactActionsFormatter(value, row, index) {return _artifactActionsFormatter(value, row, index)}

const _artifactActionsFormatter = (value, row, index) => {
    return `<a href="${getTableUrlArtifacts()}/${row['name']}" class="fa fa-download" download="${row['name']}"></a>`
}
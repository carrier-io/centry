$("#buckets-list").on('load-success.bs.table', function(e, data, status, type) {
    $("#buckets-list").bootstrapTable('check', 0);
})

$("#buckets-list").on('check.bs.table', function(e, row, element) {
    $("#bucket-name").text(row.name);
    $("#artifact-list").bootstrapTable('refresh', {url: `/api/v1/artifact/${getSelectedProjectId()}/${row.name}`});
})
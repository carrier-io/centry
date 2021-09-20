$("#buckets-list").on('load-success.bs.table', function(e, data, status, type) {
    $("#buckets-list").bootstrapTable('check', 0);
})

$("#buckets-list").on('check.bs.table', function(e, row, element) {
    $("#bucket-name").text(row.name);
    $("#artifact-list").bootstrapTable('refresh', {url: `/api/v1/artifact/${getSelectedProjectId()}/${row.name}`});
})

function allowDrop(event) {
  event.preventDefault();
}

function uploadFiles(e) {
    e.preventDefault();
    e.stopPropagation();
    files = e.dataTransfer.files;
    files.forEach(function(file) {
        _uploadFile(file);
    })
}


function _uploadFile(file) {
    let formData = new FormData()
    formData.append('file', file)
    $.ajax({
        url: `/api/v1/artifact/${getSelectedProjectId()}/${$("#bucket-name").text()}`,
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (result) {
            $("#artifact-list").bootstrapTable('refresh');
            $("#buckets-list").bootstrapTable('refresh');
        }
    });
}

function deleteBucket(event) {
    $("#buckets-list").bootstrapTable('getSelections').forEach(item => {
        $.ajax({
            url: `/api/v1/artifact/${getSelectedProjectId()}/${item["name"]}`,
            type: 'DELETE',
            success: function (result) {
                $("#buckets-list").bootstrapTable('refresh');
            }
        });
    })
}


function createBucket() {
    var expirationValue = $("#expiration-value").val();
    $.ajax({
        url: `/api/v1/artifact/${getSelectedProjectId()}`,
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(
            {
                "name": $("#bucketName").val(),
                "expiration_measure": $("#expiration-measure").val(),
                "expiration_value": !expirationValue ? null : expirationValue
            }
        ),
        success: function (result) {
            $('label[for="event"]').parent().parent().popover("hide");
            $("#buckets-list").bootstrapTable('refresh');
        },
        error: function (result) {
            console.log(result);
        }
    });
}


function deleteFiles(ev) {
    var url = `/api/v1/artifact/${getSelectedProjectId()}/${$("#bucket-name").text()}?`
    if ($("#artifact-list").bootstrapTable('getSelections').length > 0) {
        $("#artifact-list").bootstrapTable('getSelections').forEach(item => {
            url += "fname[]=" + item["name"] + "&"
        });
        $.ajax({
            url: url.substring(0, url.length - 1),
            type: 'DELETE',
            success: function (result) {
                $("#artifact-list").bootstrapTable('refresh');
                $("#buckets-list").bootstrapTable('refresh');
            }
        });
    }
}

$(document).ready(function() {
    $("[data-toggle=popover]").popover({
        sanitizeFn: function(content) {return content}
    });
});
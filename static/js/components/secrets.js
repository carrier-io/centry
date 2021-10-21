function addSecret(ev) {
    _updateSecret($("#secret_key").val(), $("#secret_value").val())
    $.ajax({
        url: `/api/v1/secrets/${getSelectedProjectId()}/${$("#secret_key").val()}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(secret_data),
        success: function (result) {
            $("#secret_value").val("");
            $("#secret_key").val("");
            $('label[for="event"]').parent().parent().popover("hide");
            $("#secrets").bootstrapTable('refresh');
        }
    });
}

function editSecret(key) {
    var cell = $(`#${key}`).parent();
    $(`#${key}`).hide();
    cell.prepend(`
        <form class="form-inline m-0">
            <input type="text" class="form-control flex-grow-1 m-0" id="edit_value" placeholder="Secret">
            <button type="button" class="btn btn-37 btn-action mL-1" onclick="updateSecret('${key}')"><i class="fas fa-check"></i></button>
            <button type="button" class="btn btn-37 btn-action mL-1" onclick="cancelUpdate('${key}')"><i class="fas fa-times"></i></button>
        </form>
    `)
}


function cancelUpdate(key) {
    $(`#${key}`).parent().find("form").remove();
    $(`#${key}`).show();
}

function updateSecret(key) {
    var value = $("#edit_value").val()
    cancelUpdate(key)
    _updateSecret(key, value)
}

function _updateSecret(key, value) {
    var secret_data = {
        secret: value
    }
    $.ajax({
        url: `/api/v1/secrets/${getSelectedProjectId()}/${key}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(secret_data),
        success: function (result) {
            $("#secret_value").val("");
            $("#secret_key").val("");
            $('label[for="event"]').parent().parent().popover("hide");
            $("#secrets").bootstrapTable('refresh');
        }
    });
}

function displaySecret(key, clipboard) {
    if ($(`#${key}`).text() === "******") {
        $.ajax({
            url: `/api/v1/secrets/${getSelectedProjectId()}/${key}`,
            type: 'GET',
            contentType: 'application/json',
            success: function (result) {
                if (!clipboard) {
                    $(`#${key}`).text(result.secret);
                } else {
                    console.log("Copied");
                }
            }
        });
    } else {
        $(`#${key}`).text("******")
    }
}

function deleteSecret(key) {
    $.ajax({
        url: `/api/v1/secrets/${getSelectedProjectId()}/${key}`,
        type: 'DELETE',
        contentType: 'application/json',
        success: function (result) {
            $("#secrets").bootstrapTable('refresh');
        }
    });
}

function viewValue(value, row, index) {
    return `<span id="${row.name}" style="display:block; width:calc(50vw); word-wrap:break-all; white-space: normal;">${value}</span>`
}

function hideSecret(key) {
    $.ajax({
        url: `/api/v1/secrets/${getSelectedProjectId()}/${key}`,
        type: 'PUT',
        contentType: 'application/json',
        success: function (result) {
            $("#secrets").bootstrapTable('refresh');
        }
    });
}

function secretsActionFormatter(value, row, index) {
    var key = row.name;
    return `
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Show"
            onclick="displaySecret('${key}', false)"><i class="far fa-eye"></i></button>
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Edit"
            onclick="editSecret('${key}')"><i class="fas fa-pen"></i></button>
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Hide"
            onclick="hideSecret('${key}')"><i class="fas fa-lock"></i></button>
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Delete"
            onclick="deleteSecret('${key}')"><i class="fa fa-trash"></i></button>
    `
}

$(document).ready(function () {
    $("[data-toggle=popover]").popover({
        sanitizeFn: function (content) {
            return content
        }
    });
    $('#secrets').bootstrapTable({
      onLoadSuccess: () => $('[data-toggle="tooltip"]').tooltip()
    })

});
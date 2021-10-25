function addSecret(ev) {
    const [secretKey, secretValue] = [$("#secret_key").val(), $("#secret_value").val()]
    _updateSecret(secretKey, secretValue)
    $.ajax({
        url: `/api/v1/secrets/${getSelectedProjectId()}/${$("#secret_key").val()}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({secret: secretValue}),
        success: function (result) {
            $("#secret_value").val("");
            $("#secret_key").val("");
            // $('label[for="event"]').parent().parent().popover("hide");
            $("#secrets_add[data-toggle=popover]").popover('hide')
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
    $.ajax({
        url: `/api/v1/secrets/${getSelectedProjectId()}/${key}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({secret: value}),
        success: function (result) {
            $("#secret_value").val("");
            $("#secret_key").val("");
            // $('label[for="event"]').parent().parent().popover("hide");
            $("#secrets_add[data-toggle=popover]").popover('hide')
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
    displayModal(
        'Delete secret?',
        `Please confirm that you want to delete ${key}`,
        () => {
            fetch(`/api/v1/secrets/${getSelectedProjectId()}/${key}`, {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'}
            }).then(response => {
                if (response.ok) {
                    $('[data-toggle="tooltip"]').tooltip('hide')
                    $("#secrets").bootstrapTable('refresh')
                }
            })
        },
        'Delete'
    )
}

function viewValue(value, row, index) {
    return `<span id="${row.name}" style="display:block; width:calc(50vw); word-wrap:break-all; white-space: normal;">${value}</span>`
}

function hideSecret(key) {
    displayModal(
        'Hide secret?',
        `Please confirm that you want to hide ${key}`,
        () => {
            fetch(`/api/v1/secrets/${getSelectedProjectId()}/${key}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'}
            }).then(response => {
                if (response.ok) {
                    $('[data-toggle="tooltip"]').tooltip('hide')
                    $("#secrets").bootstrapTable('refresh')
                }
            })
        },
        'Hide'
    )
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


const displayModal = (title, body, onOkCallback, okBtnText = 'OK') => {
    console.log('modal', {title, body, onOkCallback, okBtnText})
    $('#secrets_modal_title').text(title)
    $('#secrets_modal_body').text(body)
    $('#modal_save').text(okBtnText).prop('onclick', null).off('click').on('click', () => {
        onOkCallback()
        $('#secrets_modal').modal('hide')
    })
    $('#secrets_modal').modal('show')
}


$(document).ready(function () {
    $("#secrets_add[data-toggle=popover]").popover({
        sanitizeFn: function (content) {
            return content
        },
        content: `
            <h9 class="form-control-label" for="secret_key">Name</h9>
            <input type="text" id="secret_key" class="form-control form-control-alternative" placeholder="Name">
            
            <h9 class="form-control-label mt-1" htmlFor="secret_value">Value</h9>
            <input type="text" id="secret_value" class="form-control form-control-alternative" placeholder="Value">
            <button type="button" onClick="addSecret(event)" class="btn btn-secondary">
                Add
            </button>
            <button type="button" class="btn btn-secondary" onclick="$('#secrets_add[data-toggle=popover]').popover('hide')">
                Cancel
            </button>
        `,
        html: true
    });
    $('#secrets').bootstrapTable({
        onLoadSuccess: () => $('[data-toggle="tooltip"]').tooltip()
    })
});
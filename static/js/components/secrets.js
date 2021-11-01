const SECRET_DEFAULT_VALUE = '******'

function addSecret(ev) {
    const [secretKey, secretValue] = [$("#secret_key").val(), $("#secret_value").val()]
    createOrUpdate(secretKey, secretValue)
}

function editSecret(key, value, index) {
    $('#secrets').bootstrapTable('updateCell', {
        index: index,
        field: 'is_edited',
        value: true
    }).bootstrapTable('updateCell', {
        index: index,
        field: 'secret',
        value: `
            <form class="form-inline m-0 secret_editor">
                <input type="text" class="form-control flex-grow-1 m-0" id='edit_secret_${key}' placeholder="Secret">
                <button type="button" class="btn btn-37 btn-action mL-1" onclick="updateSecret('${key}')"><i class="fas fa-check"></i></button>
                <button type="button" class="btn btn-37 btn-action mL-1" onclick="cancelUpdate('${value}', '${index}')"><i class="fas fa-times"></i></button>
            </form>
        `
    })
}


function cancelUpdate(restoredValue, index) {
    $('#secrets').bootstrapTable('updateCell', {
        index: index,
        field: 'secret',
        value: restoredValue
    }).bootstrapTable('updateCell', {
        index: index,
        field: 'is_edited',
        value: false
    })
}

function updateSecret(key) {
    const newValue = $(`#edit_secret_${key}`).val()
    createOrUpdate(key, newValue).then(response => {
        response.ok && cancelUpdate(newValue)
    })
}


const createOrUpdate = (key, value) => {
    return fetch(`/api/v1/secrets/${getSelectedProjectId()}/${key}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({secret: value})
    }).then(r => {
        if (r.ok) {
            $('#secret_value').val('');
            $('#secret_key').val('');
            // $('label[for="event"]').parent().parent().popover("hide");
            $('#secrets_add[data-toggle=popover]').popover('hide')
            $('#secrets').bootstrapTable('refresh');
        }
    })
}

function displaySecret(key, value, index, clipboard = false) {
    if (value === SECRET_DEFAULT_VALUE) {
        fetch(`/api/v1/secrets/${getSelectedProjectId()}/${key}`).then(response => {
            if (response.ok) {
                if (clipboard) {
                    console.log('Copied')
                } else {
                    response.json().then(({secret}) => $('#secrets').bootstrapTable('updateCell', {
                        index: index,
                        field: 'secret',
                        value: secret
                    }))
                }

            }
        })
    } else {
        $('#secrets').bootstrapTable('updateCell', {
            index: index,
            field: 'secret',
            value: SECRET_DEFAULT_VALUE
        })
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
                    // $('[data-toggle="tooltip"]').tooltip('hide')
                    $("#secrets").bootstrapTable('refresh')
                }
            })
        },
        'Delete'
    )
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
                    // $('[data-toggle="tooltip"]').tooltip('hide')
                    $("#secrets").bootstrapTable('refresh')
                }
            })
        },
        'Hide'
    )
}

function secretsActionFormatter(value, row, index) {
    const key = row.name;
    const val = row.secret;
    // removing stuck tooltips
    $('div.tooltip').remove()
    if (row.is_edited) {return ''}
    return `
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Show"
            onclick="displaySecret('${key}', '${val}', '${index}', false)"><i class="far fa-eye"></i></button>
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Edit"
            onclick="editSecret('${key}', '${val}', '${index}')"><i class="fas fa-pen"></i></button>
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Hide"
            onclick="hideSecret('${key}')"><i class="fas fa-lock"></i></button>
        <button type="button" class="btn btn-24 btn-action" 
            data-toggle="tooltip" data-placement="top" title="Delete"
            onclick="deleteSecret('${key}')"><i class="fa fa-trash"></i></button>
    `
}


const displayModal = (title, body, onOkCallback, okBtnText = 'OK') => {
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
        onPostBody: () => {
            console.log('onPostBody')
            $('[data-toggle="tooltip"]').tooltip()
        }
    })

    $('#bulk_delete_secrets').on('click', () => {
        const selection = $('#secrets').bootstrapTable('getSelections').map(item => item.name)
        displayModal(
        'Delete secrets?',
        `Please confirm that you want to delete selected secrets: ${selection.join(', ')}`,
        () => {
            selection && fetch(`/api/v1/secrets/bulk_delete/${getSelectedProjectId()}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({secrets: selection})
            }).then(response => {
                response.ok && $("#secrets").bootstrapTable('refresh') && console.log('bulk deleted')
            })
        },
        'Delete selected'
    )
    })
});
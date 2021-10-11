// var scanners_cards = {};
// var edit_test = false;


function test_name_button(value, row, index) {
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('module', 'Result');
    searchParams.set('page', 'list');
    searchParams.set('project_id', getSelectedProjectId());
    searchParams.set('result_test_id', row.id);
    searchParams.set('test_id', row.test_id);
    return `<a class="test form-control-label" href="?${searchParams.toString()}" role="button">${row.name}</a>`
}

const badgeClasses = {
    'badge-dark': 0,
    'badge-light': 0,
    'badge-info': 0,
    'badge-warning': 0,
    'badge-danger': 0,
    'badge-success': 0,
    'badge-secondary': 0,
    'badge-primary': 0,
}

let tagBadgeMapping = {}

const getTagBadge = tag => {
    const tagLower = tag.toLowerCase()
    if (tagBadgeMapping[tagLower] === undefined) {
        const leastChosenClassName = Object.keys(badgeClasses).reduce(
            (className, current, index, item) =>
                badgeClasses[className] < badgeClasses[current] ? className : current
        )
        tagBadgeMapping[tagLower] = leastChosenClassName
        badgeClasses[leastChosenClassName]++
    }
    return tagBadgeMapping[tagLower]
}

function reportsTagFormatter(value, row, index) {
    const result = value?.map(item => {
        return `<span class="badge badge-pill ${getTagBadge(item)}">${item}</span>`
    })
    return result?.join(' ')
}

function reportsStatusFormatter(value, row, index) {
    switch (value.toLowerCase()) {
        case 'error':
        case 'failed':
            return `<div style="color: var(--red)">${value} <i class="fas fa-exclamation-circle error"></i></div>`
        case 'stopped':
            return `<div style="color: var(--yellow)">${value} <i class="fas fa-exclamation-triangle"></i></div>`
        case 'aborted':
            return `<div style="color: var(--gray)">${value} <i class="fas fa-times-circle"></i></div>`
        case 'finished':
            return `<div style="color: var(--info)">${value} <i class="fas fa-check-circle"></i></div>`
        case 'passed':
            return `<div style="color: var(--green)">${value} <i class="fas fa-check-circle"></i></div>`
        case 'pending...':
            return `<div style="color: var(--basic)">${value} <i class="fas fa-spinner fa-spin fa-secondary"></i></div>`
        default:
            return value
    }
}

function testActions(value, row, index) {
    return `
        <div class="d-flex justify-content-end">
            <button type="button" class="btn btn-16 btn-action run"><i class="fas fa-play"></i></button>
            <div class="dropdown action-menu">
                <button type="button" class="btn btn-16 btn-action" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
                <div class="dropdown-menu bulkActions" aria-labelledby="bulkActionsBtn">
                    <a class="dropdown-item submenu" href="#"><i class="fas fa-share-alt fa-secondary fa-xs"></i> Integrate with</a>
                    <div class="dropdown-menu">
                        <a class="dropdown-item" href="#" onclick="console.log('Docker command')">Docker command</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Jenkins stage')">Jenkins stage</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Azure DevOps yaml')">Azure DevOps yaml</a>
                        <a class="dropdown-item" href="#" onclick="console.log('Test UID')">Test UID</a>
                    </div>
                    <a class="dropdown-item settings" href="#"><i class="fas fa-cog fa-secondary fa-xs"></i> Settings</a>
                    <a class="dropdown-item trash" href="#"><i class="fas fa-trash-alt fa-secondary fa-xs"></i> Delete</a>
                </div>
            </div>
        </div>
        `
}

function cellStyle(value, row, index) {
    return {css: {"min-width": "165px"}}
}


const runTest = (id, name) => {
    console.log('Run test', id)
    fetch(`/api/v1/security/${getSelectedProjectId()}/dast/${id}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'test_name': name})
    }).then(response => response.ok && $("#results-list").bootstrapTable('refresh'))
}

const deleteTest = id => {
    const url = `/api/v1/security/${getSelectedProjectId()}/dast?` + $.param({"id[]": id})
    console.log('Delete test with id', id, url);
    fetch(url, {
        method: 'DELETE'
    }).then(response => response.ok && $("#tests-list").bootstrapTable('refresh'))
}

var statusEvents = {
    "click .run": function (e, value, row, index) {
        runTest(row.id, row.name)
    },

    "click .settings": function (e, value, row, index) {
        setModalData(row)
        // edit_test = row['test_uid'];
        $('#security_test_save').on('click', () => {
            const data = collectModalData()
            console.log('Editing test with data', data)
            // editTest(row['test_uid'], data)
        })
        $('#security_test_save_and_run').on('click', () => {
            const data = collectModalData()
            console.log('Editing and running test with data', data)
            // createAndRunTest(row['test_uid'], data)
        })
        $("#createApplicationTest").modal('show');

    },

//     "click .integrations": function (e, value, row, index) {
//         alert('You click INTEGRATIONS action')
// //        TODO: write this method
//     },

    "click .trash": function (e, value, row, index) {
        deleteTest(row.id)
    }
}


const editTest = (testUID, data) => {
    beforeSaveTest()
    fetch(`/api/v1/security/${getSelectedProjectId()}/dast/${testUID}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }).then(response => {
        afterSaveTest()
        response.ok && $("#createApplicationTest").modal('hide');
    })
}

const editAndRunTest = (testUID, data) => {
    beforeSaveTest()
    data['run_test'] = true
    fetch(`/api/v1/security/${getSelectedProjectId()}/dast/${testUID}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }).then(response => {
        afterSaveTest()
        response.ok && $("#createApplicationTest").modal('hide');
    })
}


const createTest = data => {
    beforeSaveTest()
    fetch(`/api/v1/security/${getSelectedProjectId()}/dast`, {
        method: 'POST',
        body: JSON.stringify(data)
    }).then(response => {
        afterSaveTest()
        response.ok && $("#createApplicationTest").modal('hide');
    })
}

const createAndRunTest = data => {
    beforeSaveTest()
    data['run_test'] = true
    fetch(`/api/v1/security/${getSelectedProjectId()}/dast`, {
        method: 'POST',
        body: JSON.stringify(data)
    }).then(response => {
        afterSaveTest()
        response.ok && $("#createApplicationTest").modal('hide');
    })
}

const beforeSaveTest = () => {
    $("#security_test_save").addClass("disabled updating");
    $("#security_test_save_and_run").addClass("disabled updating");
}

const afterSaveTest = () => {
    $("#tests-list").bootstrapTable('refresh');
    $("#results-list").bootstrapTable('refresh');
}

$('#createApplicationTest').on('hide.bs.modal', function (e) {
    $("#security_test_save").prop("onclick", null).off("click").removeClass("disabled updating");
    $("#security_test_save_and_run").prop("onclick", null).off("click").removeClass("disabled updating");
    clearModal()
});



// function submitAppTest(run_test = false) {
// $("#security_test_save").html(`<span class="spinner-border spinner-border-sm"></span>`);
// $("#security_test_save_and_run").html(`<span class="spinner-border spinner-border-sm"></span>`);


// //      Main variables
//     var urls_params = [[], []]
//     var run_test = run_test
//     var processing_cards = {"minimal_security_filter": null}
//
// //      Urls to scan and extensions
//     $("#url_to_scan .row").each(function (_, item) {
//         var url_ = $(item).find('input[type=text]')
//         urls_params[0].push(url_.val())
//     })
//     $("#exclusions .row").slice(1,).each(function (_, item) {
//         var url_ = $(item).find('input[type=text]')
//         urls_params[1].push(url_.val())
//     })
//
// //      --Scanner's cards--
//     getScannersData();
//
// //      --Processing's cards--
// //      Min security filter
//     processing_cards["minimal_security_filter"] = $("#severity").val()
//
//     var data = new FormData();
//
//     data.append('name', $('#testname').val());
//     // data.append('project_name', document.getElementById("selected-project").textContent);
//     data.append('project_name', getProjectNameFromId(getSelectedProjectId()));
//     data.append('test_env', $("#test_env").val());
//     data.append('urls_to_scan', JSON.stringify(urls_params[0]));
//     data.append('urls_exclusions', JSON.stringify(urls_params[1]));
//     data.append('scanners_cards', JSON.stringify(scanners_cards));
//     data.append('reporting', JSON.stringify({}));
//     data.append('processing', JSON.stringify(processing_cards));
//     data.append('run_test', run_test)

//      TODO: write reporting cards parser
//      var reporting_cards = reportingCards()
//      data.append("reporting_cards", JSON.stringify(reporting_cards))

//     saveTest(data)
// }


var deleteParams = index => {
    console.log('deleting index', index)
}


const modalDataModel = {
    name: {
        get: () => $('#test_name').val(),
        set: value => $('#test_name').val(value),
        clear: () => $('#test_name').val('')
    },
    description: {
        get: () => $('#test_description').val(),
        set: value => $('#test_description').val(value),
        clear: () => $('#test_description').val('')
    },
    parameters: {
        get: () => $('#params_list').bootstrapTable('getData'),
        set: values => console.log('SET PARAMETERS', values),
        clear: () => console.log('CLEARING TEST PARAMS TABLE')
    },
    integrations: {
        get: () => (
            $('.integration_section').toArray().reduce((accum, item) => {
                const sectionElement = $(item)
                const sectionName = sectionElement.find('.integration_section_name').text().toLowerCase().replace(' ', '_')

                const sectionData = sectionElement.find('.security_scanner').toArray().reduce((acc, i) => {
                    const integrationName = $(i).attr('data-name')
                    const dataCallbackName = `${sectionName}_${integrationName}`
                    const integrationData = window[dataCallbackName]?.get_data()
                    if (integrationData) {
                        acc[integrationName] = integrationData
                    }
                    return acc
                }, {})

                if (Object.entries(sectionData).length) {
                    accum[sectionName] = sectionData
                }
                return accum;
            }, {})
        ),
        set: values => {
            console.log('SET integrations', values)
            // {
            //     scanners: {
            //         qualys:
            //         {
            //             id: "44"
            //         }
            //     }
            // }

            $('.integration_section').toArray().forEach(item => {
                const sectionElement = $(item)
                const sectionName = sectionElement.find('.integration_section_name').text().toLowerCase().replace(' ', '_')
                const sectionData = values[sectionName]
                if (sectionData) {
                    sectionElement.find('.security_scanner').toArray().forEach(i => {
                        const integrationName = $(i).attr('data-name')
                        const dataCallbackName = `${sectionName}_${integrationName}`
                        window[dataCallbackName]?.set_data(sectionData)
                    })
                }
            })
        },
        clear: () => (
            $('.integration_section').toArray().forEach(item => {
                const sectionElement = $(item)
                const sectionName = sectionElement.find('.integration_section_name').text().toLowerCase().replace(' ', '_')
                sectionElement.find('.security_scanner').toArray().forEach(i => {
                    const integrationName = $(i).attr('data-name')
                    const dataCallbackName = `${sectionName}_${integrationName}`
                    window[dataCallbackName]?.clear_data()
                })
            })
        ),
        default: {}
    },

    processing: {
        get: processing_all.get_data,
        set: processing_all.set_data,
        clear: processing_all.clear_data
    }
}


const collectModalData = () => {
    let data = {}
    Object.keys(modalDataModel).forEach(item => {
        data[item] = modalDataModel[item].get()
    })
    return data
}

const setModalData = data => {
    console.log('setModalData', data)
    const {name, processing,} = data
    modalDataModel.name.set(name)
    modalDataModel.processing.set(processing)

}

const clearModal = () => Object.keys(modalDataModel).forEach(item => {
    modalDataModel[item].clear()
})

$(document).ready(function () {

    $('#create_test').on('click', () => {
        $('#security_test_save').on('click', () => {
            const data = collectModalData()
            console.log('Creating test with data', data)
            // createTest(data)
        })
        $('#security_test_save_and_run').on('click', () => {
            const data = collectModalData()
            console.log('Creating and running test with data', data)
            // createAndRunTest(data)
        })
    })

})
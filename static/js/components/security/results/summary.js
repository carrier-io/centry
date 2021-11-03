const updateSummary = async () => {
    const testId = new URLSearchParams(location.search).get('result_test_id')
    const response = await fetch(`/api/v1/security/${getSelectedProjectId()}/dast/${testId}`)
    const data = await response.json()

    // console.log('New data', data)

    $('[data-updatable-field]').toArray().forEach(item => {
        const $item = $(item)
        const fieldName = $item.attr('data-updatable-field')
        $item.text(data[fieldName])
    })
}

const reRunTest = () => {
    let search = new URLSearchParams(location.search)
    const testId = search.get('result_test_id')
    fetch(`/api/v1/security/rerun/${testId}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            response.json().then(({result_id}) => {
                search.set('result_test_id', result_id)
                alertMain.add(`Test rerun successful! Check out the <a href="/?${search}">result page</a>`, 'success-overlay', true)
            })
        } else {
            response.text().then(data => {
                alertMain.add(data, 'danger')
            })
        }
    })
}


$( document ).on( 'updateSummaryEvent', updateSummary);

$( document ).ready(() => {
    $('#show_config_btn').on('click', () => {
        $('#showConfigModal button').attr('disabled', true)
        $('#showConfigModal button[data-toggle=collapse]').attr('disabled', false)
        $('#showConfigModal button[data-dismiss=modal]').attr('disabled', false)
        $('#showConfigModal input').attr('disabled', true)
        $('#showConfigModal input[type=text]').attr('readonly', true)
    })

    $('#re_run_test').on('click', reRunTest)
})
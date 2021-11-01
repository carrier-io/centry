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



$( document ).on( 'updateSummaryEvent', updateSummary);

$( document ).ready(() => {
    $('#show_config_btn').on('click', () => {
        $('#showConfigModal button').attr('disabled', true)
        $('#showConfigModal button[data-toggle=collapse]').attr('disabled', false)
        $('#showConfigModal input').attr('disabled', true)
        $('#showConfigModal input[type=text]').attr('readonly', true)

    })
})
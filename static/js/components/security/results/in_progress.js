const updateStatus = async () => {
    const testId = new URLSearchParams(location.search).get('result_test_id')
    const response = await fetch(`/api/v1/security/${getSelectedProjectId()}/dast/${testId}`)
    const { test_status: { status, percentage, description } } = await response.json()

    $('#test_status_status').text(status)
    $('#test_status_description').text(description)
    $(".space-progress .progress-bar").css('width', `${percentage}%`).attr('aria-valuenow', percentage)

    return { status, percentage, description }
}

$(document).ready(() => {
    const intrvl = setInterval(() => {
        updateStatus().then(({ percentage }) => {
            if (percentage === 100) {
                clearInterval(intrvl)
                location.reload()
            }
        })
    }, 1000)
})
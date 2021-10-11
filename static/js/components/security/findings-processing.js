window['processing_all'] = {
    get_data: () => {
        return {
            minimal_security_filter: $('#MSF .selectpicker').val(),
        }
    },
    set_data: data => {
        $('#MSF .selectpicker').val(data.minimal_security_filter).selectpicker('refresh')
    },
    clear_data: () => {
        $('#MSF .selectpicker').val('Info').selectpicker('refresh')
    }
}
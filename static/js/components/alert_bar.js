class AlertBar {
    alertVariants = [
        'primary', 'secondary',
        'success', 'danger',
        'warning', 'info',
        'light', 'dark'
    ]
    alertIdIndex = 1

    constructor(containerId) {
        this.containerId = containerId;
        this.$alertContainer = $(`#${containerId}`)
        this.$alertContainerOverlay = this.$alertContainer.find('.overlaying')
        this.maxAlerts = this.$alertContainer.attr('data-max-alerts') || 1
    }

    getAlerts = () => this.$alertContainer.find('.alert')

    clear = () => this.getAlerts().alert('close')

    add = (
        body,
        variant = 'info',
        closeable = true,
        closeIn = 0
    ) => {

        const [variantOriginal, isOverlayed] = variant.toLowerCase().split('-')

        if (!this.alertVariants.includes(variantOriginal)) {
            throw new Error(`Alert variant "${variant}" is not in available ${JSON.stringify(this.alertVariants)}`);
        }

        const alertBarId = `alert_bar_${this.alertIdIndex}`
        this.alertIdIndex++

        const closeBtn = `
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `

        const $alerts = this.getAlerts()
        $alerts.length >= this.maxAlerts && $alerts.first().alert('close')

        if (isOverlayed) {
            this.$alertContainerOverlay.append(`
                <div 
                    class="alert alert-${variantOriginal} alert-dismissible fade show" 
                    role="alert" 
                    id="${alertBarId}" 
                >
                        ${body}
                        ${closeable ? closeBtn : ''}
                </div>
            `)
        } else {
            this.$alertContainerOverlay.before(`
                <div 
                    class="alert alert-${variantOriginal} alert-dismissible fade show" 
                    role="alert" 
                    id="${alertBarId}" 
                >
                        ${body}
                        ${closeable ? closeBtn : ''}
                </div>
            `)
        }


        if (closeIn > 0) {
            const $countdown = $(`#${alertBarId}`).find('.countdown')
            let intrvl = -1
            if ($countdown.length > 0) {
                let ticks = Math.floor(closeIn / 1000)
                $countdown.text(ticks)
                ticks--
                intrvl = setInterval(() => {
                    $countdown.text(ticks)
                    ticks--
                }, 1000)
            }
            setTimeout(() => {
                clearInterval(intrvl)
                $(`#${alertBarId}`).alert('close')
            }, closeIn)
        }

    }
}

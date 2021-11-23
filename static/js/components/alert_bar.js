class AlertBar {
    static alertVariants = [
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
        this.maxAlerts = parseInt(this.maxAlerts)
    }

    getAlerts = () => this.$alertContainer.find('.alert').sort((a, b)=> parseInt(a.id.split('_')[2]) - parseInt(b.id.split('_')[2]))

    clear = () => this.getAlerts().alert('close')

    add = (
        body,
        variant = 'info',
        closeable = true,
        closeIn = 0
    ) => {

        const [variantOriginal, isOverlaid] = variant.toLowerCase().split('-', 2)

        if (!AlertBar.alertVariants.includes(variantOriginal)) {
            throw new Error(`Alert variant "${variant}" is not in available: ${JSON.stringify(AlertBar.alertVariants)}`);
        }

        const alertBarId = `alert_bar_${this.alertIdIndex}`
        this.alertIdIndex++

        const closeBtn = `
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `

        const $alerts = this.getAlerts()
        if ($alerts.length >= this.maxAlerts) {
            $alerts.splice($alerts.length - this.maxAlerts + 1)
            $alerts.alert('close')
        }

        if (isOverlaid === 'overlay') {
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

if (Boolean(AlertBar.alertVariants.find(item => item.includes('-')))) {
    throw new Error(`
        Alert variants should not contain "-" symbol. 
        Consider renaming or removing: ${AlertBar.alertVariants.filter(item => item.includes('-'))}
    `);
}

function lgFormatter(value, row, index) {
    if (value === "perfmeter") {
        return '<img src="assets/ico/jmeter.png" width="20">'
    } else if (value === "perfgun") {
        return '<img src="assets/ico/gatling.png" width="20">'
    } else {
        return value
    }
}

function actionFormatter(value, row, index) {
    return `
    <div class="d-flex justify-content-end">
        <button type="button" class="btn btn-16 btn-action"><i class="fas fa-play"></i></button>
        <button type="button" class="btn btn-16 btn-action"><i class="fas fa-cog"></i></button>
        <button type="button" class="btn btn-16 btn-action"><i class="fas fa-share-alt"></i></button>
        <button type="button" class="btn btn-16 btn-action"><i class="fas fa-trash-alt"></i></button>
    </div>
    `
}

function nameStyle(value, row, index) {
    return {css: {"max-width": "100px", "overflow": "hidden", "text-overflow": "ellipsis", "white-space": "nowrap"}}
}
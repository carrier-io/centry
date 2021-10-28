const selectedProjectLocalStorageKey = 'selectedProject';

const getSelectedProjectId = () => {
    let projectId = localStorage.getItem(selectedProjectLocalStorageKey);
    if (projectId === null) {
        projectId = getSelectedProjectIdFromBackend().then(id => parseInt(id));
    }
    return parseInt(projectId)
}

function toggleAdvanced(id) {
    $(`#${id}`).toggle();
}

function removeParam(ev) {
    if (ev.target.parentNode.parentNode.classList.contains("flex-row")) {
        ev.target.parentNode.parentNode.remove();
    } else {
        ev.target.parentNode.parentNode.parentNode.remove();
    }

}

function addParam(id, key="", value="") {
    $(`#${id}`).append(`<div class="d-flex flex-row">
    <div class="flex-fill">
        <input type="text" class="form-control form-control-alternative" placeholder="${key}">
    </div>
    <div class="flex-fill pl-3">
        <input type="text" class="form-control form-control-alternative" placeholder="${value}">
    </div>
    <div class="m-auto pl-3">
        <button type="button" class="btn btn-32 btn-action" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
    </div>
</div>`)
}

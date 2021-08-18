var backendUrl = '/api/v1/project-session';
var projectSelectId = '#projectSelect';


async function setSelectedProjectOnBackend(projectId) {
    const resp = await fetch(`${backendUrl}/${projectId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: {}
    });
    if (resp.ok) {
        return await resp.json()
    }

}


async function getSelectedProjectIdFromBackend() {
    const resp = await fetch(backendUrl);
    if (resp.ok) {
        const projectData = await resp.json();
        return projectData.id
    }
    return null
}


function getProjectNameFromId(projectId) {
    return $(projectSelectId).find(`[project_id=${projectId}]`).val()
}


function setSelectedProjectOnPage(projectId) {
    localStorage.setItem(selectedProjectLocalStorageKey, projectId);
    $(projectSelectId).selectpicker('val', getProjectNameFromId(projectId))
}


async function loadProject() {
    const projectId = await getSelectedProjectIdFromBackend();
    setSelectedProjectOnPage(projectId);
};


async function setProject(projectId) {
    localStorage.setItem(selectedProjectLocalStorageKey, projectId);
    const responseMessage = setSelectedProjectOnBackend(projectId);
    console.log(await responseMessage);
};


$(document).ready(() => {
    // Chapter dropdown init
    $('#chapterSelect').on('change', event => {
        const searchParams = new URLSearchParams(location.search);
        searchParams.set('chapter', event.target.value);
        location.search = searchParams.toString();
    })

    // Project dropdown init
    loadProject();
    $(projectSelectId).on('change', event => {
        setProject($(event.target).find(':selected').attr('project_id')).then(() => location.reload())
    });
})
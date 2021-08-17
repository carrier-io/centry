const backendUrl = '/api/v1/project-session';
const projectSelectId = '#projectSelect';


const setSelectedProjectOnBackend = async projectId => {
    const resp = await fetch(`${backendUrl}/${projectId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: {}
    });
    if (resp.ok) {
        return await resp.json()
    }

}


const getSelectedProjectIdFromBackend = async () => {
    const resp = await fetch(backendUrl);
    if (resp.ok) {
        const projectData = await resp.json();
        return projectData.id
    }
    return null
}


const getProjectNameFromId = projectId => {
    return $(projectSelectId).find(`[project_id=${projectId}]`).val()
}


const setSelectedProjectOnPage = projectId => {
    localStorage.setItem(selectedProjectLocalStorageKey, projectId);
    $(projectSelectId).selectpicker('val', getProjectNameFromId(projectId))
}


const loadProject = async () => {
    const projectId = await getSelectedProjectIdFromBackend();
    setSelectedProjectOnPage(projectId);
};


const setProject = async projectId => {
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
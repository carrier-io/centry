const selectedProjectLocalStorageKey = 'selectedProject';

const getSelectedProjectId = () => {
    let projectId = localStorage.getItem(selectedProjectLocalStorageKey);
    if (projectId === null) {
        projectId = getSelectedProjectIdFromBackend().then(id => parseInt(id));
    }
    return parseInt(projectId)
}
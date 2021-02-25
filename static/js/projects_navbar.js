(function () {
    let projectsDropdown = document.getElementById("projects-dropdown");
    let projectsDropdownItems = document.getElementById("projects-dropdown-items");
    let selectedProjectTitle = document.getElementById("selected-project");
    let selectedProjectId = document.getElementById("selected-project-id");

    function fillSelectedProject(projectData) {
        if (projectData instanceof Object) {
            selectedProjectId.textContent = projectData.id;
            selectedProjectTitle.textContent = projectData.name;
        }
    }

    function initProjectDropdown(projectData) {
        if (projectData === undefined) {
            let request = new XMLHttpRequest();
            request.open("GET", "/api/v1/project-session", false);  // `false` makes the request synchronous
            request.send();
            if (request.status === 200) {
                projectData = JSON.parse(request.responseText);
            }
            if (request.status === 404) {
                fillDropdown();
            }
        }
        fillSelectedProject(projectData);
    }

    function setUserSession() {
        try {
            let req = new XMLHttpRequest();
            req.open("GET", `/forward-auth/me`, false);
            req.send();
            if (req.status === 200) {
                let request = new XMLHttpRequest();
                request.open("POST", `/api/v1/project-session`, false);  // `false` makes the request synchronous
                request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                request.send(req.responseText);
                if (request.status === 200) {
                    return false;
                }
            }
            return false;
        } catch (err) {
            console.log("Request Error :-S", err);
        }
    }

    function selectSessionProject(projectData) {
        try {
            let req = new XMLHttpRequest();
            req.open("GET", `/forward-auth/me`, false);
            req.send();
            if (req.status === 200) {
                let request = new XMLHttpRequest();
                request.open("POST", `/api/v1/project-session/${projectData.id}`, false);  // `false` makes the request synchronous
                request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                request.send(req.responseText);
                if (request.status === 200) {
                    projectData = JSON.parse(request.responseText);
                    initProjectDropdown(projectData);
                    window.location.reload();
                    return false;
                }
            }
            return false;
        } catch (err) {
            console.log("Request Error :-S", err);
        }
    }

    function fillDropdown() {
        while (projectsDropdownItems.firstChild) {
            projectsDropdownItems.removeChild(projectsDropdownItems.firstChild);
        }
        try {
            let request = new XMLHttpRequest();
            request.open("GET", `/api/v1/project`, false);  // `false` makes the request synchronous
            request.send();
            if (request.status === 200) {
                let projectsData = JSON.parse(request.responseText);
                for (let projectData of projectsData) {
                    let aElement = document.createElement("a");
                    aElement.setAttribute("class", "dropdown-item");
                    let spanElement = document.createElement("span");
                    let projectNameText = document.createTextNode(projectData.name);
                    spanElement.appendChild(projectNameText);
                    aElement.appendChild(spanElement);
                    aElement.addEventListener(
                        "click",
                        () => selectSessionProject(projectData), false
                    );
                    projectsDropdownItems.appendChild(aElement);
                }
            }
        } catch (err) {
            console.log("Request Error :-S", err);
        }
    }

    initProjectDropdown();
    setUserSession();
    projectsDropdown.addEventListener("click", fillDropdown, false);

    window.getSelectedProjectId = function () {
        return selectedProjectId.textContent
    };
    window.selectSessionProject = selectSessionProject;
})();

$(".main-nav .nav-link").on("click", function(ev) {
    $(".main-nav .nav-link").removeClass("current");
    ev.target.classList.add("current");
})

function selectProject(projectData) {
    document.getElementById("selected-project").textContent = projectData.name
    document.getElementById("selected-project-id").textContent = projectData.id
}

$(".select-project").on("click", function(ev) {
    selectProject({name: ev.target.textContent, id: ev.target.getAttribute("project-id")})
})

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

// Test planner
function addParam(id, key="", value="") {
    $(`#${id}`).append(`<div class="row mt-2">
    <div class="col">
        <input type="text" class="form-control" placeholder="Variable name" value="${key}">
    </div>
    <div class="col">
        <input type="text" class="form-control" placeholder="Value" value="${value}">
    </div>
    <div class="col-xs text-right">
        <button type="button" class="btn btn-nooutline-secondary mt-2 mr-2" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
    </div>
</div>`)
}

function removeParam(ev) {
    if (ev.target.parentNode.parentNode.classList.contains("row")) {
        ev.target.parentNode.parentNode.remove();
    } else {
        ev.target.parentNode.parentNode.parentNode.remove();
    }

}

function getSelectedProjectId() {
    return parseInt($("#selected-project-id").text())
}

function toggleRows(id) {
    if ($(`#${id} .row.hidden`).length == 0) {
        $(`#${id} .row`).slice(1,).addClass("hidden")
    } else {
        $(`#${id} .row.hidden`).removeClass("hidden")
    }
}

$(".email").change(function() {
    if (this.checked) {
      $("#email_input").show();
    } else {
      $("#email_input").hide();
    }
  });


function toggleAdvanced(id) {
    $(`#${id}`).toggle();
}
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

function closePopover(e) {
    $('label[for="event"]').parent().parent().popover("hide");
}

// Test planner
function addParam(id, key="", value="") {
    $(`#${id}`).append(`<div class="row mt-2">
    <div class="col ml-0 pl-0">
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

function addThreeParam(id, condition="", key="", value="") {
    $(`#${id}`).append(`<div class="row mt-2">
    <div class="col ml-0 pl-0">
        <input type="text" class="form-control" placeholder="Condition" value="${condition}">
    </div>
    <div class="col">
        <input type="text" class="form-control" placeholder="Variable name" value="${key}">
    </div>
    <div class="col">
        <input type="text" class="form-control" placeholder="Value" value="${value}">
    </div>
    <div class="col-xs text-right">
        <button type="button" class="btn btn-nooutline-secondary mt-2" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
    </div>
</div>`)
}

function addNewURL(id, value_="e.g.https://mysiteaddress.com"){
    $(`#${id}`).append(`<div class="row mt-2 ml-3">
    <div class="col pl-0 pr-0">
        <input type="text" class="form-control" placeholder="${value_}">
    </div>
    <div class="col-xs text-right">
        <button type="button" class="btn btn-nooutline-secondary mt-2 mr-2" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
    </div>
</div>`)
//    $(`#${id}`).append(`
//    <div class="form-group pl-1 mb-0 mt-0">
//        <input type="text" class="form-control" placeholder="${value_}">
//    </div>
//    <div class="col-xs text-right">
//        <button type="button" class="btn btn-nooutline-secondary mt-2 mr-2" onclick="removeParam(event)"><i class="fas fa-minus"></i></button>
//    </div>
//`)
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

function selectProject(ev){
    $.ajax({
        url: `/api/v1/project-session/${ev.getAttribute('project_id')}`,
        type: 'POST',
        contentType: 'application/json',
        data: {},
        success: function (result) {
            window.location.href = '/';
        }
    })
}
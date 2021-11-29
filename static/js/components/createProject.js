$(document).ready(function() {
    class divFieldset extends HTMLElement {
        constructor() {
            // Always call super first in constructor
            super();
        }
    }
    class divFigure extends HTMLElement {
        constructor() {
            // Always call super first in constructor
            super();
        }
    }

    class divContent extends HTMLElement {
        constructor() {
            // Always call super first in constructor
            super();
        }
    }

    customElements.define('div-fieldset', divFieldset)
    customElements.define('div-figure', divFigure)
    customElements.define('div-content', divContent)

    noUiSlider.create($("#vuh-slider")[0], {
        start: 500,
        range: {
            'min': 500,
            'max': 60000
        },
        step: 500,
        format: wNumb({
            decimals: 0
        }),
         pips: {
            mode: 'values',
            values: [500, 5000, 20000, 40000, 60000],
            density: 3
        }
    })
    $("#vuh-slider")[0].noUiSlider.on('update', function (values, handle, unencoded, isTap, positions) {
        var vuh = parseInt(values[handle])
        var cost = vuh === 500 ? "FREE" : `${vuh * 0.1} $`
        $("#vuh").text(vuh);
        $("#cost").text(cost);
    })
    renderUsersProjects();
})

function renderUsersProjects() {
    $.ajax({
        url: `/api/v1/project?offset=0`,
        type: 'GET',
        contentType: 'application/json',
        success: function (result) {
            console.log(result)
            if (result.length > 0){
                $(".current .actions").parent().append(`<h3 class='mt-3 mb-2 w-100 align-middle' style="text-align: center;">or select project</h3><div id='projectSelect' class='scrollable-list-group mt-2'>
                    <div class="list-group">
                    </div>
                </div>`)
                result.forEach(function(item) {
                    $("#projectSelect .list-group").append(`<button type="button" class="list-group-item list-group-item-sm list-group-item-action" onclick="selectProject(${item.id})" project_id=${item.id}>${item.name}</button>`)
                })
            }
        }
    });
}

function selectProject(project_id){
    setProject(project_id).then(() => document.location.href="/";);
}
(function($) {
    var original_steps = "";
    var form = $("#create-project");
    form.steps({
        headerTag: "h3",
        bodyTag: "div-fieldset",
        actionContainerTag: "div-steps",
        labels: {
            previous: 'Prev',
            next: 'Next',
            finish: 'Finish',
            current: ''
        },
        onInit: function(even, currentIndex) {
            $("div-steps").insertAfter($(".current .col").last().children().last());
            $('div-steps a[href="#next"]').parent().siblings().hide()
            $('div-steps a[href="#next"]').addClass("w-100")
            $('div-steps a[href="#next"]').parent().addClass("w-100 m-0")
            $('div-steps a[href="#next"]').text("Create Project")
        },
        onStepChanging: function (event, currentIndex, newIndex)
        {
            if (newIndex == 0) {
                $('div-steps a[href="#next"]').parent().siblings().hide()
                $('div-steps a[href="#next"]').addClass("w-100")
                $('div-steps a[href="#next"]').parent().addClass("w-100 m-0")
                $('div-steps a[href="#next"]').text("Create Project")
            } else if (newIndex > 0 && $('div-steps a[href="#next"]').parent().hasClass("w-100")) {
                $('div-steps a[href="#next"]').removeClass("w-100")
                $('div-steps a[href="#next"]').parent().hasClass("w-10")
                $('div-steps a[href="#next"]').parent().removeClass("w-100")
                $('div-steps a[href="#next"]').parent().removeClass("m-0")
                $('div-steps a[href="#next"]').parent().siblings().show()
                $('div-steps a[href="#previous"]').text("Back")
                $('div-steps a[href="#previous"]').addClass("btn-secondary")
                $('div-steps a[href="#previous"]').addClass("m-0")
                $('div-steps a[href="#previous"]').parent().addClass("margin-right-auto")
                $('div-steps a[href="#next"]').text("Continue")
            }
            if(currentIndex === 0) {
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-0');
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-1');
                form.find('.content .body .step-current-content').append('<span class="step-inner step-inner-' + currentIndex + '"></span>');
            }
            if(currentIndex === 1 || currentIndex === 2) {
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-0').addClass('step-inner-'+ currentIndex + '');
            }
            $("div-steps").insertAfter($(`#create-project-p-${newIndex} .col`).last().children().last());
            return true;
        },
        onFinished: function(event, currentIndex) {
            var plugins = []
            $('input[type="checkbox"]:checked').each(function(index, item){
                plugins.push(item.id)
            })
            var project_data = {
                name: $("#project_name").val(),
                owner: "",
                vuh_limit: $("#vuh-slider")[0].noUiSlider.get(),
                plugins: plugins
            }
            $.ajax({
                url: `/api/v1/project`,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(project_data),
                success: function (result) {
                    window.location.href = "/?chapter=Configuration&module=Tasks&page=list"
                }
            });
        }
    });

    $(".toggle-password").on('click', function() {

        $(this).toggleClass("zmdi-eye zmdi-eye-off");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });

})(jQuery);
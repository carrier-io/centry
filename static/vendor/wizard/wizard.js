(function($) {

    var form = $("#create-project");
    form.steps({
        headerTag: "h3",
        bodyTag: "fieldset",
        labels: {
            previous: 'Prev',
            next: 'Next',
            finish: 'Finish',
            current: ''
        },
        titleTemplate: '<h3 class="title">#title#</h3>',
        onStepChanging: function (event, currentIndex, newIndex)
        {
            if(currentIndex === 0) {

                form.find('.content .body .step-current-content').find('.step-inner').removeClass('.step-inner-0');
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('.step-inner-1');
                form.find('.content .body .step-current-content').append('<span class="step-inner step-inner-' + currentIndex + '"></span>');
            }
            if(currentIndex === 1 || currentIndex === 2) {
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-0').addClass('step-inner-'+ currentIndex + '');
            }
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
                    window.location.href = "/?chapter=Manage%20Project"
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
(function ($) {
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
        onInit: function (even, currentIndex) {
            $("div-steps").insertAfter($(".current .col").last().children().last());
            $('div-steps a[href="#next"]').parent().siblings().hide()
            $('div-steps a[href="#next"]').addClass("w-100")
            $('div-steps a[href="#next"]').parent().addClass("w-100 m-0")
            $('div-steps a[href="#next"]').text("Create Project")
        },
        onStepChanging: function (event, currentIndex, newIndex) {
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
            if (currentIndex === 0) {
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-0');
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-1');
                form.find('.content .body .step-current-content').append('<span class="step-inner step-inner-' + currentIndex + '"></span>');
            }
            if (currentIndex === 1 || currentIndex === 2) {
                form.find('.content .body .step-current-content').find('.step-inner').removeClass('step-inner-0').addClass('step-inner-' + currentIndex + '');
            }
            $("div-steps").insertAfter($(`#create-project-p-${newIndex} .col`).last().children().last());
            return true;
        },
        onFinished: function (event, currentIndex) {
            var plugins = []
            $('input[type="checkbox"]:checked').each(function (index, item) {
                plugins.push(item.id)
            })
            var project_data = {
                name: $("#project_name").val(),
                owner: "",
                vuh_limit: $("#vuh-slider")[0].noUiSlider.get(),
                plugins: plugins,
                invitations: vm.$data.invitations
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

    $(".toggle-password").on('click', function () {

        $(this).toggleClass("zmdi-eye zmdi-eye-off");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });

})(jQuery);

const app = Vue.createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                placeholderText: 'User email (e.g.: John.Doe@gmail.com)',
                email: '',
                group: '',
                invitations: [],
                error: '',
            }
        },
        mounted() {
            try {
                this.group = this.$refs.groupSelect.options[0].value;
            } catch (e) {

            }
        },
        computed: {
            invitation() {
                return {email: this.email, group: this.group};
            }
        },
        methods: {
            onEmailInputChange(event) {
                this.email = event.target.value;
            },
            handleAdd() {
                if (this.email === '') return;
                if (!this.validateEmail()) {
                    this.error = 'Please enter a valid email';
                    return;
                }
                if (!this.validateUniqueness()) {
                    this.error = 'Invitation is already added';
                    return;
                }
                this.invitations.push(this.invitation);
                this.email = this.error = '';

            },
            validateUniqueness() {
                return this.invitations.find(inv => inv.email.toLowerCase() === this.email.toLowerCase() && inv.group.toLowerCase() === this.group.toLowerCase()) === undefined;
            },
            validateEmail() {
                return /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(this.email);
            },
            removeListItem(index) {
                this.invitations.splice(index, 1);
            }
        }

    })
;

const vm = app.mount('#invitations');


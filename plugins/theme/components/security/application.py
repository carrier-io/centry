from flask import request, render_template


def applications_scanners_config(context, slot, payload):
    return render_template(
        f"security/app/application-scanners.html",
        config=payload
    )

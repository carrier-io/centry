from flask import request, render_template


def findings_processing(context, slot, payload):
    return render_template(
        f"security/app/findings-processing.html",
        config=payload
    )

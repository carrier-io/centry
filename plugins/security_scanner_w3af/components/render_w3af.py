from flask import request, render_template


def render_w3af_card(context, slot, payload):
    return render_template(
        f"w3af_template.html",
        config=payload
    )
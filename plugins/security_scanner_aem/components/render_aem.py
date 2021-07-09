from flask import request, render_template


def render_aem_card(context, slot, payload):
    return render_template(
        f"aem_template.html",
        config=payload
    )

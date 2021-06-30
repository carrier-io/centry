from flask import request, render_template


def render_sslyze_card(context, slot, payload):
    return render_template(
        f"sslyze_template.html",
        config=payload
    )

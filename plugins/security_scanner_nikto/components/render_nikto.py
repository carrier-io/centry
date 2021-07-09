from flask import render_template


def render_nikto_card(context, slot, payload):
    return render_template(
        f"nikto_template.html",
        config=payload
    )

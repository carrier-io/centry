from flask import request, render_template


def render_masscan_card(context, slot, payload):
    return render_template(
        f"masscan_template.html",
        config=payload
    )

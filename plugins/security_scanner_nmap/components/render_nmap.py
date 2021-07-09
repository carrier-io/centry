from flask import request, render_template


def render_nmap_card(context, slot, payload):
    return render_template(
        f"nmap_template.html",
        config=payload
    )

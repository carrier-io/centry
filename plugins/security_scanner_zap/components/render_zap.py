from flask import request, render_template
import os


def render_zap_card(context, slot, payload):
    return render_template(
        f"zap_template.html",
        config=payload
    )
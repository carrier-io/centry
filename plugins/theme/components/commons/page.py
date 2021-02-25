import logging
from flask import request, render_template
from traceback import format_exc


def render_page(context, slot, payload):  # pylint: disable=R0201,W0613
    """ Base template slot """
    chapter = request.args.get('chapter', '')
    page = request.args.get('page', '')
    try:
        return render_template(f"{chapter.lower()}/{page}.html", active_chapter=chapter, config=payload)
    except:
        return render_template(f"common/empty.html", active_chapter=chapter, config=payload)

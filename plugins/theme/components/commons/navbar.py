from flask import request, render_template


def render_navbar(context, slot, payload):  # pylint: disable=R0201,W0613
    """ Base template slot """
    chapter = request.args.get('chapter', '')
    module = request.args.get('module', '')
    return render_template("common/navbar.html", active_chapter=chapter, module=module, config=payload)

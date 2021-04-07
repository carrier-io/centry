import logging
from flask import request, render_template
from traceback import format_exc


def render_page(context, slot, payload):  # pylint: disable=R0201,W0613
    """ Base template slot """
    chapter = request.args.get('chapter', '')
    module = request.args.get('module', '')
    page = request.args.get('page', '')
    try:
        if page:
            return render_template(f"{chapter.lower()}/{module.lower()}/{page.lower()}.html", active_chapter=chapter,
                                   config=payload)
        return render_template(f"{chapter.lower()}/{module.lower()}.html", active_chapter=chapter, config=payload)
    except:
        return render_template(f"common/empty.html", active_chapter=chapter, config=payload)


def render_test(context, slot, payload):  # pylint: disable=R0201,W0613
    """ Base template slot """
    chapter = request.args.get('chapter', '')
    module = request.args.get('module', '')
    try:
        if module:
            return render_template(f"{chapter.lower()}/{module.lower()}/create.html", active_chapter=chapter,
                                   config=payload)
        return render_template(f"{chapter.lower()}/create.html", active_chapter=chapter, config=payload)
    except:
        return render_template(f"common/empty.html", active_chapter=chapter, config=payload)


def reporting_config(context, slot, payload):
    return render_template(f"common/reporting-config.html", config=payload)


def applications_scanners_config(context, slot, payload):
    # templates = [
    #     {"name": "Template_1", "id": 1},
    #     {"name": "Template_2", "id": 2},
    #     {"name": "Template_3", "id": 3},
    # ]
    # payload["templates"] = templates
    return render_template(f"security/app/application-scanners.html", config=payload)


def findings_processing(context, slot, payload):
    return render_template(f"security/app/findings-processing.html", config=payload)

from flask import request, render_template


def result_findings(context, slot, payload):
    return render_template(
        f"security/result/findings_table.html",
        config=payload
    )


def result_artifacts(context, slot, payload):
    return render_template(
        f"security/result/artifacts_table.html",
        config=payload
    )


def tests_logs(context, slot, payload):
    return render_template(
        f"security/result/logs_list.html",
        config=payload
    )

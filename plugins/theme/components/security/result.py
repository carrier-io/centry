from flask import request, render_template

from pylon.core.tools import log
from pylon.core.tools.minio import MinIOHelper
from plugins.project.connectors.secrets import get_project_hidden_secrets


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

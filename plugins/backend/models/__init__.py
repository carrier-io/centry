
def unsecret(app, secret, project_id):
    app.config["rpc"].call("project", "unsecret", value=secret, project_id=project_id)
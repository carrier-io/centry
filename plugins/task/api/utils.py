from uuid import uuid4
from time import mktime
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import Forbidden

from arbiter import Arbiter

from plugins.base.constants import RABBIT_HOST, RABBIT_PORT, RABBIT_USER, RABBIT_PASSWORD, RABBIT_QUEUE_NAME
from plugins.base.utils.api_utils import upload_file
from plugins.base.data_utils.file_utils import File
from ..models.tasks import Task
from ..models.results import Results


def get_arbiter():
    arbiter = Arbiter(host=RABBIT_HOST, port=RABBIT_PORT, user=RABBIT_USER, password=RABBIT_PASSWORD)
    return arbiter


def create_task(project, file, args):
    if isinstance(file, str):
        file = File(file)
    filename = str(uuid4())
    filename = secure_filename(filename)
    upload_file(bucket="tasks", f=file, project=project)
    task = Task(
        task_id=filename,
        project_id=project["id"],
        zippath=f"tasks/{file.filename}",
        task_name=args.get("funcname"),
        task_handler=args.get("invoke_func"),
        runtime=args.get("runtime"),
        env_vars=args.get("env_vars")
    )
    task.insert()
    return task


def check_task_quota(task, project_id=None, quota='tasks_executions'):
    project_id = project_id if project_id else task["project_id"]
    from flask import current_app
    if not current_app.context.rpc_manager.call_function('project_check_quota', project_id=project_id, quota=quota):
        data = {"ts": int(mktime(datetime.utcnow().timetuple())), 'results': 'Forbidden',
                'stderr': f'The number of {quota} allowed in the project has been exceeded'}
        if task:
            headers = {
                "Content-Type": "application/json",
                "Token": task['token']
            }
            auth_token = current_app.context.rpc_manager.call_function(
                'project_unsecret',
                value="{{secret.auth_token}}",
                project_id=task['project_id']
            )
            if auth_token:
                headers['Authorization'] = f'bearer {auth_token}'

            task.set_last_run(data["ts"])
            result = Results(task_id=task["id"], project_id=project_id, ts=data["ts"], results=data["results"],
                             log=data["stderr"])
            result.insert()
        raise Forbidden(description=f"The number of {quota} allowed in the project has been exceeded")
    else:
        return {"message", "ok"}


def run_task(project_id, event, task_id=None):
    from flask import current_app
    secrets = current_app.context.rpc_manager.call_function('project_get_secrets', project_id=project_id)
    if "control_tower_id" not in secrets:
        secrets = current_app.context.rpc_manager.call_function('project_get_hidden_secrets', project_id=project_id)
    task_id = task_id if task_id else secrets["control_tower_id"]
    task = Task.query.filter(and_(Task.task_id == task_id)).first().to_json()
    check_task_quota(task)
    statistic = Statistic.query.filter(Statistic.project_id == task['project_id']).first()
    setattr(statistic, 'tasks_executions', Statistic.tasks_executions + 1)
    statistic.commit()
    arbiter = get_arbiter()
    task_kwargs = {
        "task": current_app.context.rpc_manager.call_function(
            'project_unsecret',
            value=task,
            project_id=project_id
        ),
        "event": current_app.context.rpc_manager.call_function(
            'project_unsecret',
            value=event,
            project_id=project_id
        ),
        "galloper_url": current_app.context.rpc_manager.call_function(
            'project_unsecret',
            value="{{secret.galloper_url}}",
            project_id=task['project_id']
        ),
        "token": current_app.context.rpc_manager.call_function(
            'project_unsecret',
            value="{{secret.auth_token}}",
            project_id=task['project_id']
        )
    }
    arbiter.apply("execute_lambda", queue=RABBIT_QUEUE_NAME, task_kwargs=task_kwargs)
    arbiter.close()
    return {"message": "Accepted", "code": 200, "task_id": task_id}

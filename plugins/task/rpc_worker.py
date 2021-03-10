from arbiter import Minion
from plugins.base import constants as c
from .models.tasks import Task
from .api.utils import create_task
import logging
minion = Minion(host=c.RABBIT_HOST, port=c.RABBIT_PORT, user=c.RABBIT_USER,
                password=c.RABBIT_PASSWORD, queue="task")


@minion.task(name="list")
def list_projects(project_id):
    return Task.list_tasks(project_id)


@minion.task(name="create")
def create(project_id, filename, args):
    logging.info(f"Filename: {filename}")
    return create_task(project_id, filename, args).to_json()

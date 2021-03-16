import logging
from plugins.task.models.tasks import Task
from plugins.task.api.utils import create_task


def tasks_count(project_id):
    return Task.tasks_count(project_id)


def list_tasks(project_id):
    return Task.list_tasks(project_id)


def create(project, filename, args):
    logging.info(f"Filename: {filename}")
    return create_task(project, filename, args)
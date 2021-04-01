from plugins.project.models.project import Project, SessionProject, get_user_projects
from plugins.project.models.quota import ProjectQuota
from plugins.project.models.statistics import Statistic


def prj_or_404(project_id):
    return Project.get_or_404(project_id)


def list_projects():
    return Project.list_projects()


def get_project_statistics(project_id):
    return Statistic.query.filter_by(project_id=project_id).first().to_json()


def add_task_execution(project_id):
    statistic = Statistic.query.filter_by(project_id=project_id).first()
    setattr(statistic, 'tasks_executions', Statistic.tasks_executions + 1)
    statistic.commit()


def get_storage_quota(project_id):
    return Project.get_storage_space_quota(project_id=project_id)


def check_quota(project_id, quota=None):
    return ProjectQuota.check_quota_json(project_id, quota)


def get_project_config(project_id=None):
    if project_id:
        project_id = SessionProject.get()
    if not project_id:
        project_id = get_user_projects()[0]["id"]
    try:
        return Project.query.filter_by(project_id=project_id).first().to_json()
    except:
        return {}

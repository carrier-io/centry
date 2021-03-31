from plugins.project.models.project import Project, SessionProject, get_user_projects
from plugins.project.models.quota import ProjectQuota
from plugins.project.models.statistics import Statistic
from plugins.project.connectors.secrets import unsecret, get_project_hidden_secrets, set_project_secrets, \
    set_project_hidden_secrets, get_project_secrets


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


def unsecret_key(value, secrets=None, project_id=None):
    unsecret(value, secrets=secrets, project_id=project_id)


def get_hidden(project_id):
    return get_project_hidden_secrets(project_id=project_id)


def get_secrets(project_id):
    return get_project_secrets(project_id=project_id)


def set_hidden(project_id, secrets):
    return set_project_hidden_secrets(project_id, secrets=secrets)


def set_secrets(project_id, secrets):
    return set_project_secrets(project_id, secrets=secrets)


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

# from arbiter import Minion
# from plugins.base import constants as c
from plugins.project.models.project import Project
from plugins.project.models.quota import ProjectQuota
from plugins.project.models.statistics import Statistic
from plugins.project.connectors.secrets import unsecret, get_project_hidden_secrets, set_project_secrets, set_project_hidden_secrets

# minion = Minion(host=c.RABBIT_HOST, port=c.RABBIT_PORT, user=c.RABBIT_USER,
#                 password=c.RABBIT_PASSWORD, queue="project")


# @minion.task(name="get_or_404")
def prj_or_404(project_id):
    return Project.get_or_404(project_id)


# @minion.task(name="list")
def list_projects():
    return Project.list_projects()


# @minion.task(name="statistics")
def get_project_statistics(project_id):
    return Statistic.query.filter_by(project_id=project_id).first().to_json()


# @minion.task(name="get_storage_space_quota")
def get_storage_quota(project_id):
    return Project.get_storage_space_quota(project_id=project_id)


# @minion.task(name="unsecret")
def unsecret_key(value, secrets=None, project_id=None):
    unsecret(value, secrets=secrets, project_id=project_id)


# @minion.task(name="get_hidden_secrets")
def get_hidden(project_id):
    return get_project_hidden_secrets(project_id=project_id)


# @minion.task(name="set_hidden_secrets")
def set_hidden(project_id, secrets):
    return set_project_hidden_secrets(project_id, secrets=secrets)


# @minion.task(name="set_secrets")
def set_secrets(project_id, secrets):
    return set_project_secrets(project_id, secrets=secrets)


# @minion.task(name="check_quota")
def check_quota(project_id, quota=None):
    return ProjectQuota.check_quota_json(project_id, quota)

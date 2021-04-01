import hvac
import requests

from jinja2 import Template
from flask import current_app

import plugins.base.constants as c
from plugins.base.connectors.vault import create_client, get_root_client
from plugins.project.models.project import Project


def get_project_client(project_id):
    """ Get "project" Vault client instance """
    # Get Vault client
    client = create_client()
    # Get project from DB
    project = Project.query.get(project_id)
    # Auth to Vault
    client.auth_approle(
        project.secrets_json["vault_auth_role_id"], project.secrets_json["vault_auth_secret_id"],
        mount_point="carrier-approle",
    )
    # Done
    return client


def add_hidden_kv(project_id, client=None):
    # Create hidden secrets KV
    if not client:
        client = get_root_client()
    try:
        client.sys.enable_secrets_engine(
            backend_type="kv",
            path=f"kv-for-hidden-{project_id}",
            options={"version": "2"},
        )
        client.secrets.kv.v2.create_or_update_secret(
            path="project-secrets",
            mount_point=f"kv-for-hidden-{project_id}",
            secret=dict(),
        )
    except hvac.exceptions.InvalidRequest:
        pass
    return client


def set_hidden_kv_permissions(project_id, client=None):
    if not client:
        client = get_root_client()
    policy = """
        # Login with AppRole
        path "auth/approle/login" {
          capabilities = [ "create", "read" ]
        }
        # Read/write project secrets
        path "kv-for-{project_id}/*" {
          capabilities = ["create", "read", "update", "delete", "list"]
        }
        # Read/write project hidden secrets
        path "kv-for-hidden-{project_id}/*" {
          capabilities = ["create", "read", "update", "delete", "list"]
        }
    """.replace("{project_id}", str(project_id))
    client.sys.create_or_update_policy(
        name=f"policy-for-{project_id}",
        policy=policy
    )


def initialize_project_space(project_id):
    """ Create project approle, policy and KV """
    client = get_root_client()
    # Create policy for project
    set_hidden_kv_permissions(project_id, client)
    # Create secrets KV
    client.sys.enable_secrets_engine(
        backend_type="kv",
        path=f"kv-for-{project_id}",
        options={"version": "2"},
    )
    client.secrets.kv.v2.create_or_update_secret(
        path="project-secrets",
        mount_point=f"kv-for-{project_id}",
        secret=dict(),
    )
    # Create hidden secrets KV
    add_hidden_kv(project_id, client)
    # Create AppRole
    approle_name = f"role-for-{project_id}"
    requests.post(
        f"{c.VAULT_URL}/v1/auth/carrier-approle/role/{approle_name}",
        headers={"X-Vault-Token": client.token},
        json={"policies": [f"policy-for-{project_id}"]}
    )
    approle_role_id = requests.get(
        f"{c.VAULT_URL}/v1/auth/carrier-approle/role/{approle_name}/role-id",
        headers={"X-Vault-Token": client.token},
    ).json()["data"]["role_id"]
    approle_secret_id = requests.post(
        f"{c.VAULT_URL}/v1/auth/carrier-approle/role/{approle_name}/secret-id",
        headers={"X-Vault-Token": client.token},
    ).json()["data"]["secret_id"]
    # Done
    return {
        "auth_role_id": approle_role_id,
        "auth_secret_id": approle_secret_id
    }


def remove_project_space(project_id):
    """ Remove project-specific data from Vault """
    client = get_root_client()
    # Remove AppRole
    requests.delete(
        f"{c.VAULT_URL}/v1/auth/carrier-approle/role/role-for-{project_id}",
        headers={"X-Vault-Token": client.token},
    )
    # Remove secrets KV
    client.sys.disable_secrets_engine(
        path=f"kv-for-{project_id}",
    )
    # Remove hidden secrets KV
    client.sys.disable_secrets_engine(
        path=f"kv-for-hidden-{project_id}",
    )
    # Remove policy
    client.sys.delete_policy(
        name=f"policy-for-{project_id}",
    )


def set_project_secrets(project_id, secrets):
    """ Set project secrets """
    client = get_project_client(project_id)
    client.secrets.kv.v2.create_or_update_secret(
        path="project-secrets",
        mount_point=f"kv-for-{project_id}",
        secret=secrets,
    )


def set_project_hidden_secrets(project_id, secrets):
    """ Set project hidden secrets """
    try:
        client = get_project_client(project_id)
        client.secrets.kv.v2.create_or_update_secret(
            path="project-secrets",
            mount_point=f"kv-for-hidden-{project_id}",
            secret=secrets,
        )
    except (hvac.exceptions.Forbidden, hvac.exceptions.InvalidPath):
        current_app.logger.error("Exception Forbidden in set_project_hidden_secret")
        set_hidden_kv_permissions(project_id)
        return set_project_secrets(project_id, secrets)


def get_project_secrets(project_id):
    """ Get project secrets """
    client = get_project_client(project_id)
    return client.secrets.kv.v2.read_secret_version(
        path="project-secrets",
        mount_point=f"kv-for-{project_id}",
    ).get("data", dict()).get("data", dict())


def get_project_hidden_secrets(project_id):
    """ Get project hidden secrets """
    client = get_project_client(project_id)
    try:
        return client.secrets.kv.v2.read_secret_version(
            path="project-secrets",
            mount_point=f"kv-for-hidden-{project_id}",
        ).get("data", dict()).get("data", dict())
    except (hvac.exceptions.Forbidden, hvac.exceptions.InvalidPath):
        current_app.logger.error("Exception Forbidden in get_project_hidden_secret")
        set_hidden_kv_permissions(project_id)
        return {}


def unsecret(value, secrets=None, project_id=None):
    if not secrets:
        secrets = get_project_secrets(project_id)
        hidden_secrets = get_project_hidden_secrets(project_id)
        for key, _value in hidden_secrets.items():
            if key not in list(secrets.keys()):
                secrets[key] = _value
    if isinstance(value, str):
        template = Template(value)
        return template.render(secret=secrets)
    elif isinstance(value, list):
        return unsecret_list(secrets, value)
    elif isinstance(value, dict):
        return unsecret_json(secrets, value)
    else:
        return value


def unsecret_json(secrets, json):
    for key in json.keys():
        json[key] = unsecret(json[key], secrets)
    return json


def unsecret_list(secrets, array):
    for i in range(len(array)):
        array[i] = unsecret(array[i], secrets)
    return array

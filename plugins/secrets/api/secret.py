from typing import Tuple
from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from ..connectors.secrets import (get_project_secrets, set_project_secrets,
                                  get_project_hidden_secrets, set_project_hidden_secrets)


class SecretApi(RestResource):  # pylint: disable=C0111
    post_rules = (
        dict(name="secret", type=str, required=True, default=None, location="json"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_post = build_req_parser(rules=self.post_rules)

    def get(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=R0201,C0111
        # Check project_id for validity
        project = self.rpc.project_get_or_404(project_id)
        # Get secret
        secrets = get_project_secrets(project.id)
        _secret = secrets.get(secret) if secrets.get(secret) else get_project_hidden_secrets(project.id).get(secret)
        return {"secret": _secret}, 200

    def post(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        data = self._parser_post.parse_args()
        # Check project_id for validity
        project = self.rpc.project_get_or_404(project_id)
        # Set secret
        secrets = get_project_secrets(project.id)
        secrets[secret] = data["secret"]
        set_project_secrets(project.id, secrets)
        return {"message": f"Project secret was saved"}, 200

    def put(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        # Check project_id for validity
        project = self.rpc.project_get_or_404(project_id)
        # Set secret
        secrets = get_project_secrets(project.id)
        hidden_secrets = get_project_hidden_secrets(project.id)
        hidden_secrets[secret] = secrets[secret]
        secrets.pop(secret, None)
        set_project_secrets(project.id, secrets)
        set_project_hidden_secrets(project.id, hidden_secrets)
        return {"message": f"Project secret was moved to hidden secrets"}, 200

    def delete(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        project = self.rpc.project_get_or_404(project_id)
        secrets = get_project_secrets(project.id)
        if secret in secrets:
            del secrets[secret]
        set_project_secrets(project.id, secrets)
        return {"message": "deleted"}, 200

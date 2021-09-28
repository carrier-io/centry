from typing import List

from flask import current_app
from plugins.integrations.models.integration import Integration
from plugins.integrations.models.integration_pd import IntegrationPD

from plugins.integrations.models.registration_pd import RegistrationForm
from pydantic import parse_obj_as
from functools import reduce
from collections import defaultdict

def register(reg_dict, slot_manager, **kwargs):
    form_data = RegistrationForm(**kwargs)
    reg_dict[form_data.name] = form_data
    slot_manager.register_callback(
        f'integrations_{form_data.section}',
        form_data.integration_callback
    )


def get_integration(reg_dict, integration_name):
    return reg_dict.get(integration_name)


def get_project_integrations(project_id):
    results = Integration.query.filter(Integration.project_id == project_id).group_by(
        Integration.section,
        Integration.id
    ).all()
    results = parse_obj_as(List[IntegrationPD], results)

    def reducer(cumulative, new_value):
        cumulative[new_value.section].append(new_value)
        return cumulative

    return reduce(reducer, results, defaultdict(list))


def get_project_integrations_by_name(project_id, integration_name):
    results = Integration.query.filter(
        Integration.project_id == project_id,
        Integration.name == integration_name
    ).all()
    results = parse_obj_as(List[IntegrationPD], results)
    return results

from flask import current_app

from plugins.integrations.models.registration_pd import RegistrationForm


def register(reg_dict, slot_manager, **kwargs):
    form_data = RegistrationForm(**kwargs)
    reg_dict[form_data.name] = form_data
    slot_manager.register_callback(
        f'integrations_{form_data.section}',
        form_data.integration_callback
    )


def get_integration(reg_dict, integration_name):
    return reg_dict.get(integration_name)



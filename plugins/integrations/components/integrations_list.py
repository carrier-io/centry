from typing import List

from flask import render_template
from plugins.integrations.models.integration import Integration
from plugins.integrations.models.integration_pd import IntegrationPD
from pydantic import parse_obj_as


def render_integrations(context, slot, payload):
    # if not context.slot_manager.callbacks.get('integrations'):
    #     # log.warning("No scanners for security application were installed")
    #     return render_template(
    #         'integrations_list.html',
    #         config=payload
    #     )
    # context.slot_manager.callbacks["left_col_scanners"] = (
    #     context.slot_manager.callbacks["security_scanners"][
    #         :
    #         len(context.slot_manager.callbacks["security_scanners"]) // 2
    #     ]
    # )
    # context.slot_manager.callbacks["right_col_scanners"] = (
    #     context.slot_manager.callbacks["security_scanners"][
    #         len(context.slot_manager.callbacks["security_scanners"]) // 2:
    #     ]
    # )
    print('$'*88)
    print('C', context)
    print('S', slot)
    print('P', payload)
    print()
    print(context.rpc_manager.call.integrations_sections())
    print(context.slot_manager.callbacks.get('integrations_scanners'))
    print('$'*88)

    results = context.rpc_manager.call.integrations_get_project_integrations(payload['id'])

    print('existing_integrations', results)

    payload['existing_integrations'] = results
    payload['integrations_sections'] = {*context.rpc_manager.call.integrations_sections(), *results.keys()}

    # payload['scanners'] = "security_scanners"
    # payload["right_scanners"] = "right_col_scanners"
    # payload["left_scanners"] = "left_col_scanners"

    return render_template(
        'integrations_list.html',
        config=payload
    )

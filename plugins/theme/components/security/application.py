from flask import render_template


def applications_scanners_config(context, slot, payload):
    context.slot_manager.callbacks["left_col_scanners"] = (
        context.slot_manager.callbacks["security_scanners"][
            :
            len(context.slot_manager.callbacks["security_scanners"]) // 2
        ]
    )
    context.slot_manager.callbacks["right_col_scanners"] = (
        context.slot_manager.callbacks["security_scanners"][
            len(context.slot_manager.callbacks["security_scanners"]) // 2:
        ]
    )

    payload['scanners'] = "security_scanners"
    payload["right_scanners"] = "right_col_scanners"
    payload["left_scanners"] = "left_col_scanners"

    return render_template(
        f"security/app/application-scanners.html",
        config=payload
    )

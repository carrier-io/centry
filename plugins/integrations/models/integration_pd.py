from typing import Dict, Optional, Any, Callable

from flask import current_app

from pydantic import BaseModel, validator


class IntegrationPD(BaseModel):

    # def __init__(self, *args, **kwargs):
    #     print("INIT AAA", args, kwargs)
    #
    #     super().__init__(*args, **kwargs)
        # self.settings = self.rpc.integrations_get_integration().settings_model.parse_obj()

        # self.settings = self.rpc.integrations_get_integration().settings_model.parse_obj(self.settings)

    id: int
    name: str
    section: str
    settings: dict
    is_default: bool

    @validator("settings")
    def validate_date(cls, value, values):
        # print('VALUE', value)
        # print('VALUESSS', values)
        return current_app.config['CONTEXT'].rpc_manager.call.integrations_get_integration(
            values['name']
        ).settings_model.parse_obj(value).dict(exclude={'password'})

    class Config:
        orm_mode = True

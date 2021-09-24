from typing import Dict, Optional, Any, Callable

from pydantic.main import ModelMetaclass

from pydantic import BaseModel


class RegistrationForm(BaseModel):
    name: str
    section: str
    settings_model: ModelMetaclass
    integration_callback: Callable

    class Config:
        json_encoders = {
            ModelMetaclass: lambda v: str(type(v)),
        }
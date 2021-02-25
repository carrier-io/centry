#     Copyright 2020 getcarrier.io
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
import inspect
from abc import ABCMeta
from threading import Lock
from typing import Optional, Dict, Tuple, Callable


class SingletonMeta(type):
    _instance: Optional["SingletonABC"] = None
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class SingletonABC(SingletonMeta, ABCMeta):
    ...


class SingletonParametrizedMeta(type):
    _instances: Dict[Tuple[str, frozenset], "SingletonParametrizedABC"] = {}
    _init: Dict[str, Callable] = {}
    _lock: Lock = Lock()

    def __init__(cls, name, bases, attrs):
        cls._init[cls.__name__] = attrs.get('__init__', None)
        super().__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        init = cls._init[cls.__name__]
        if init is not None:
            key = (cls.__name__,
                   frozenset(inspect.getcallargs(init, None, *args, **kwargs).items()))
        else:
            key = cls.__name__

        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]


class SingletonParametrizedABC(SingletonParametrizedMeta, ABCMeta):
    ...

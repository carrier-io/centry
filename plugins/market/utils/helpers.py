import subprocess
import sys
from distutils import log
from pathlib import Path
from typing import Union

import pkg_resources
from pkg_resources import Requirement


def install(package: Union[Requirement, str], path: Union[Path, str] = None):
    extra_args = ['-t', str(path)] if path else []
    try:
        response = subprocess.check_call([sys.executable, '-m', 'pip', 'install', str(package), *extra_args])
        assert response == 0
    except (subprocess.CalledProcessError, AssertionError):
        log.error(f'Cannot install module {str(package)}')
        return

    dist = pkg_resources.get_distribution(package)
    return dist

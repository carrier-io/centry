import json
import site
from distutils.sysconfig import get_python_lib
from functools import partial, cached_property
from pathlib import Path

import pkg_resources
from pkg_resources import Environment

from .helpers import install


class Plugin:
    package_folder = 'site-packages'
    requirements_file = 'requirements.txt'
    metadata_file = 'metadata.json'
    directory = Path('plugins')
    global_site_packages = get_python_lib()

    def __init__(self, name):
        self.name = name
        # self.status_downloaded = self.path.exists()
        try:
            self.reload_metadata()
        except FileNotFoundError:
            self.metadata = self._metadata_default

    @property
    def status_downloaded(self):
        return self.path.exists()

    def reload_metadata(self):
        self.metadata = json.load(self.path.joinpath(self.metadata_file).open('r'))

    @property
    def _metadata_default(self):
        return {
            "name": self.name,
            "version": "0.0",
            "module": '.'.join([self.directory.stem, self.name]),
            "extract": False,
            "depends_on": [],
            "init_after": []
        }

    @property
    def path(self):
        return self.directory.joinpath(self.name)

    def create(self, rewrite=False):
        if rewrite:
            self.metadata = self._metadata_default
        if not self.path.exists() or rewrite:
            self._create()

    def _create(self):
        self.path.mkdir(exist_ok=True)
        self.path.joinpath('__init__.py').write_text('from .module import Module\n')
        json.dump(self.metadata, self.path.joinpath(self.metadata_file).open('w'), ensure_ascii=False, indent=2)
        self.requirements.touch(exist_ok=True)

    @property
    def version(self):
        return self.metadata['version']

    @property
    def sp(self):
        return self.path.joinpath(self.package_folder)

    @property
    def requirements(self):
        return self.path.joinpath(self.requirements_file)

    def register(self):
        market = self.__class__('market')
        with open(market.sp.joinpath(f'{self.name}.pth'), 'w') as out:
            out.write(str(self.sp.absolute()))
        pkg_resources.working_set.add_entry(self.sp)
        site.addsitedir(self.sp.absolute())

    def _register_in_global(self):
        with open(Path(self.global_site_packages, f'{self.name}.pth'), 'w') as out:
            out.write(f"import site; site.addsitedir(r'{self.sp.absolute()}')")
        pkg_resources.working_set.add_entry(self.sp)
        site.addsitedir(self.sp.absolute())

    @cached_property
    def environment(self):
        return Environment([str(self.sp)])

    @cached_property
    def installer(self):
        return partial(install, path=self.sp)

    def __repr__(self):
        return f'<Plugin: {self.name} v={self.version} {"RDY" if self.status_downloaded else "TDL"}>'

    def __hash__(self):
        return hash((self.name, self.version))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

import json
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

    def __init__(self, name, depends_on: list = None):
        self.name = name
        self.status_downloaded = self.path.exists()
        self._metadata = {
            "name": self.name,
            "version": "0.1",
            "module": '.'.join([self.directory.stem, self.name]),
            "extract": False,
            "depends_on": depends_on or [],
            "init_after": []
        }
        try:
            self.metadata = json.load(self.path.joinpath(self.metadata_file).open('r'))
        except FileNotFoundError:
            self.metadata = self._metadata

    @property
    def path(self):
        return self.directory.joinpath(self.name)

    def create(self, rewrite=False):
        if rewrite:
            self.metadata = self._metadata
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

    def add_entry(self):
        pkg_resources.working_set.add_entry(self.sp)

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


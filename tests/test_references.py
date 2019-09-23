import importlib
import pkgutil
from types import ModuleType
from typing import (Iterable,
                    Optional)

import requests
from _pytest.monkeypatch import MonkeyPatch
from lz.functional import identity

import gon
from gon import documentation


def test_callables(monkeypatch: MonkeyPatch) -> None:
    def documentation_setup(documented: documentation.Documented = None,
                            *,
                            reference: Optional[str] = None,
                            **_) -> documentation.Documented:
        assert (reference is None
                or all(requests.get(link,
                                    headers={'User-Agent': 'test'}).ok
                       for link in reference.splitlines()))
        if documented is not None:
            return documented
        return identity

    monkeypatch.setattr(documentation, documentation.setup.__name__,
                        documentation_setup)

    for module_name in to_submodules_names(gon):
        importlib.import_module(module_name)


def to_submodules_names(package: ModuleType) -> Iterable[str]:
    for _, module_name, _ in pkgutil.walk_packages(package.__path__,
                                                   package.__name__ + '.'):
        yield module_name

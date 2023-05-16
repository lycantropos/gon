import os
import sys
from datetime import timedelta

import pytest
from hypothesis import (HealthCheck,
                        settings)

on_ci = bool(os.getenv('CI', False))
is_pypy = sys.implementation.name == 'pypy'
max_examples = ((1 if is_pypy else 10)
                if on_ci
                else settings.default.max_examples)
settings.register_profile('default',
                          max_examples=max_examples,
                          deadline=(timedelta(hours=1) / max_examples
                                    if on_ci
                                    else None),
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session,
                         exitstatus: pytest.ExitCode) -> None:
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK

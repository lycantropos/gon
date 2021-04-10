import os
import platform
from decimal import (getcontext,
                     setcontext)

import pytest
from hypothesis import (HealthCheck,
                        settings)

from .utils import MAX_COORDINATE_EXPONENT

on_travis_ci = os.getenv('CI', False)
on_azure_pipelines = os.getenv('TF_BUILD', False)
is_pypy = platform.python_implementation() == 'PyPy'
settings.register_profile('default',
                          max_examples=(settings.default.max_examples
                                        // (10 * (1 + is_pypy))
                                        if on_travis_ci or on_azure_pipelines
                                        else settings.default.max_examples),
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])


@pytest.fixture(autouse=True,
                scope='session')
def set_decimal_context() -> None:
    # required for accurate calculation of linear length/shaped perimeter
    context = getcontext()
    context.prec = MAX_COORDINATE_EXPONENT * 5
    setcontext(context)

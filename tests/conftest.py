import os
import platform

from hypothesis import (HealthCheck,
                        settings)

on_travis_ci = os.getenv('CI', False)
on_azure_pipelines = os.getenv('TF_BUILD', False)
is_pypy = platform.python_implementation() == 'PyPy'
settings.register_profile('default',
                          max_examples=(settings.default.max_examples
                                        // (4 * (1 + is_pypy))
                                        if on_travis_ci or on_azure_pipelines
                                        else settings.default.max_examples),
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])

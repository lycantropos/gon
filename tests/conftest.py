import os
import platform

from hypothesis import (HealthCheck,
                        settings)

on_ci = bool(os.getenv('CI', False))
is_pypy = platform.python_implementation() == 'PyPy'
settings.register_profile('default',
                          max_examples=(settings.default.max_examples
                                        // (10 * (1 + 4 * is_pypy))
                                        if on_ci
                                        else settings.default.max_examples),
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])

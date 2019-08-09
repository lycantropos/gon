import os
from datetime import timedelta

from hypothesis import (HealthCheck,
                        settings)

on_travis_ci = os.getenv('CI', False)
on_azure_pipelines = os.getenv('TF_BUILD', False)
settings.register_profile('default',
                          max_examples=(25
                                        if on_travis_ci or on_azure_pipelines
                                        else settings.default.max_examples),
                          deadline=timedelta(seconds=10),
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])

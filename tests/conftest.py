from datetime import timedelta

from hypothesis import (HealthCheck,
                        settings)

settings.register_profile('default',
                          max_examples=20,
                          deadline=timedelta(seconds=10),
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])

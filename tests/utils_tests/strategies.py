from hypothesis import strategies

permutations = (strategies.builds(range,
                                  strategies.integers(min_value=1,
                                                      max_value=10 ** 4))
                .flatmap(strategies.permutations))
permutations |= permutations.map(tuple)

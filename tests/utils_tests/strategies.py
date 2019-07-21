from hypothesis import strategies

identity_permutations = strategies.builds(range,
                                          strategies.integers(min_value=1,
                                                              max_value=1000))
identity_permutations = (identity_permutations.map(list)
                         | identity_permutations.map(tuple))
permutations = identity_permutations.flatmap(strategies.permutations)
permutations |= permutations.map(tuple)

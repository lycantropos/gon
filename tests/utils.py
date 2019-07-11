from hypothesis.searchstrategy import SearchStrategy

Strategy = SearchStrategy


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent

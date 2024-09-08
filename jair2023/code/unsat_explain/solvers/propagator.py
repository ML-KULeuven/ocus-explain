
def unsat_optimal_propagate(sat, I=set(), U=None, end_time_timeout=None):
    """
    optPropage produces the intersection of all models of cnf more precise
    projected on focus.

    Improvements:
    - Extension 1:
        + Reuse solver only for optpropagate
    - Extension 2:
        + Reuse solver for all sat calls
    - Extension 3:
        + Set phases

    Args:
    cnf (list): CNF C over V:
            hard puzzle problems with assumptions variables to activate or
            de-active clues.
    I (list): partial interpretation

    U (list):
        +/- literals of all user variables
    """
    solved = sat.solve_limited(assumptions=list(I), expect_interrupt=True)

    if not solved:
        return None

    model = set(sat.get_model())
    if U:
        model = set(l for l in model if abs(l) in U)

    bi = sat.nof_vars() + 1

    while(True):
        sat.add_clause([-bi] + [-lit for lit in model])
        solved = sat.solve_limited(assumptions=list(I) + [bi], expect_interrupt=True)

        if not solved:
            sat.add_clause([-bi])
            return model

        new_model = set(sat.get_model())
        model = model.intersection(new_model)

def propagate_interpretation(U, I, sat):
    print(sat.nof_clauses())
    print(sat.nof_vars())
    assert not sat.solve(assumptions=list(I)), "Ensuring UNSAT"

    model = set(I)

    for v in U:
        if not v in I and not -v in I:
            model.add(v)

    return model
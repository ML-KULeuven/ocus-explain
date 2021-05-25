from pyexplain.solvers.params import COusParams, Grow, Interpretation, OptUxMIPParams, Weighing, OusParams
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.explain.greedy_explain import GreedyExplain
from pyexplain.utils.utils import cost_puzzle
from pyexplain.explain.optux_explain import OptUXExplain
from pyexplain.examples.frietkot import *
from pysat.formula import CNF

instance = "simple"
## CONSTRAINED OUS + INCREMENTAL
# ocusparams = Cou()


ocusparams = COusParams()

ocusparams.instance = instance
ocusparams.output = "test.json"

# running params
ocusparams.grow = Grow.MAXSAT
ocusparams.interpretation = Interpretation.ACTUAL
ocusparams.maxsat_weighing = Weighing.UNIFORM
# ocusparams.maxsat_polarity = True
ocusparams.timeout = 60

## Greedy reuse SSes 
ousGreedy = OusParams()

ousGreedy.instance = instance
ousGreedy.grow = Grow.MAXSAT
ousGreedy.interpretation = Interpretation.ACTUAL
ousGreedy.maxsat_weighing = Weighing.UNIFORM
ousGreedy.maxsat_polarity = True

# ous-specific params
ousGreedy.sort_literals = True
ousGreedy.reuse_SSes = False

puzzle_funs = {
    "origin-problem": originProblem,
    "pastaPuzzle": pastaPuzzle,
    "p12": p12,
    "p13": p13,
    "p16": p16,
    "p18": p18,
    "p25": p25,
    "p20": p20,
    "p93": p93,
    "p19": p19,
    "frietkot": frietKotProblem,
    "simple": simpleProblem
}

puzzleFun = puzzle_funs[instance]

# getting the clauses and weights
p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()

# transform to CNF object
o_cnf = CNF(from_clauses=p_clauses)

# User vocabulary
U = p_user_vars | set(x for lst in p_ass for x in lst)
print(U)

# initial interpretation
I = set(x for lst in p_ass for x in lst) | set({1})

# weight/cost of explanations
f = cost_puzzle(U, I, p_weights)

# optux_expl_computer = OptUXExplain(o_cnf, matching_table=matching_table)
# optux_expl_computer.explain(U=U, f=f, I0=I)

ocus_expl_computer = OCUSExplain(C=o_cnf, params=ocusparams, matching_table=matching_table, verbose=True)
ocus_expl_computer.explain(U=U, f=f, I0=I)

# ous_expl_computer = GreedyExplain(C=o_cnf, params=ousGreedy, matching_table=matching_table, verbose=True)
# ous_expl_computer.explain(U=U, f=f, I0=I)

# copt_expl_computer = COptUxExplain(C=o_cnf, params=ocusparams, matching_table=matching_table, verbose=True)
# copt_expl_computer.explain(U=U, f=f, I0=I)


# optux_mip_params = OptUxMIPParams()
# optux_mip_explainer = OptUXMIPExplain(C=o_cnf, params=optux_mip_params, verbose=True)
# optux_mip_explainer.explain(U=U, f=f, I0=I)

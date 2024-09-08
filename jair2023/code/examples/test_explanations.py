from pyexplain.explain.parallel_greedy_incr_naive_explain import ParallelGreedyIncrNaiveExplain
from pyexplain.explain.mus_explain import MUSExplain
from pyexplain.solvers.params import COusParams, DisjointMCSes, Grow, Interpretation, MUSParams, OUSParallelIncrNaiveParams, OusIncrNaiveParams, OusNoOptParams, Weighing
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.utils.utils import cost_puzzle
from pyexplain.examples.frietkot import *
from pysat.formula import CNF

## CONSTRAINED OUS + INCREMENTAL
# ocusparams = Cou()
puzzle_funs = {
    "frietkot": frietKotProblem,
    "simple": simpleProblem,
    "origin-problem": originProblem,
    "pastaPuzzle": pastaPuzzle,
    "p12": p12,
    "p13": p13,
    "p16": p16,
    "p18": p18,
    "p25": p25,
    "p20": p20,
    "p93": p93,
    "p19": p19
}
instance="simple"
puzzleFun = puzzle_funs[instance]

ocus_params = COusParams()
ocus_params.maxsat_weighing = Weighing.UNIFORM
ocus_params.interpretation = Interpretation.ACTUAL
ocus_params.grow = Grow.MAXSAT
ocus_params.disjoint_mcs_interpretation = None
ocus_params.disjoint_mcs_weighing = None
ocus_params.disjoint_mcses = DisjointMCSes.DISABLED
ocus_params.maxsat_polarity = True
ocus_params.instance = instance
ocus_params.output = "ocus.json"


# iter_no_bootstrapping = OUSParallelIncrNaiveParams()
# iter_no_bootstrapping.grow = Grow.CORR_GREEDY
# iter_no_bootstrapping.disjoint_mcs_interpretation = Interpretation.ACTUAL
# iter_no_bootstrapping.disjoint_mcs_weighing = Weighing.UNIFORM
# iter_no_bootstrapping.disjoint_mcs_weighing = Weighing.UNIFORM
# iter_no_bootstrapping.instance = instance
# iter_no_bootstrapping.output = "iter_no_bootstrapping.json"

# iter_with_bootstrapping = OUSParallelIncrNaiveParams()
# iter_with_bootstrapping.grow = Grow.CORR_GREEDY
# iter_with_bootstrapping.disjoint_mcses = DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY
# iter_with_bootstrapping.disjoint_mcs_interpretation = Interpretation.ACTUAL
# iter_with_bootstrapping.disjoint_mcs_weighing = Weighing.UNIFORM
# iter_with_bootstrapping.instance = instance
# iter_with_bootstrapping.output = "iter_with_bootstrapping.json"

# getting the clauses and weights
p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()
matching_table = None

# transform to CNF object
o_cnf = CNF(from_clauses=p_clauses)

# User vocabulary
U = p_user_vars | set(x for lst in p_ass for x in lst)
# print(U)

# initial interpretation
I = set(x for lst in p_ass for x in lst)

# weight/cost of explanations
f = cost_puzzle(U, I, p_weights)

expl_computer = OCUSExplain(C=o_cnf, params=ocus_params, matching_table=matching_table, verbose=3)
expl_seq = expl_computer.explain(U=U, f=f, I0=I)
# iter_no_bootstrapping_expl_computer = ParallelGreedyIncrNaiveExplain(C=o_cnf, params=iter_no_bootstrapping, matching_table=matching_table, verbose=3)
# iter_with_bootstrapping_expl_computer = ParallelGreedyIncrNaiveExplain(C=o_cnf, params=iter_with_bootstrapping, matching_table=matching_table, verbose=3)

# expl_sequence = iter_no_bootstrapping_expl_computer.explain(U=U, f=f, I0=I)
# expl_sequence = iter_with_bootstrapping_expl_computer.explain(U=U, f=f, I0=I)

from pyexplain.solvers.params import COusParams,
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.explain.greedy_explain import GreedyExplain
from pyexplain.explain.ocus_non_incr_explain import OCUSExplainNotIncremental
from pyexplain.explain.greedy_incr_naive_explain import GreedyIncrNaiveExplain
from pyexplain.explain.greedy_incr_shared_explain import GreedyIncrSharedExplain
from pyexplain.explain.mus_explain import MUSExplain
from pyexplain.utils.utils import cost_puzzle
from pyexplain.examples.frietkot import *
from pysat.formula import CNF

INSTANCE = "simple"

PUZZLE_FUNS = {
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

EXPLANATION_COMPUTERS = {
    "OCUS+Incr. HS": ,
    "OCUS": ,
    
}

## CONSTRAINED OUS + INCREMENTAL - automatically loads
## best configuration for running puzzle
ocus_params = COusParams()

puzzleFun = PUZZLE_FUNS[INSTANCE]

# getting the clauses and weights
p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()

# transform to CNF object
o_cnf = CNF(from_clauses=p_clauses)

# User vocabulary
U = p_user_vars | set(x for lst in p_ass for x in lst)

# initial interpretation
I = set(x for lst in p_ass for x in lst)

# weight/cost of explanations
f = cost_puzzle(U, I, p_weights)

ocus_expl_computer = OCUSExplain(C=o_cnf, params=ocus_params, matching_table=matching_table, verbose=True)
ocus_expl_computer.explain(U=U, f=f, I0=I)

# ous_expl_computer = GreedyExplain(C=o_cnf, params=ousGreedy, matching_table=matching_table, verbose=True)
# ous_expl_computer.explain(U=U, f=f, I0=I)


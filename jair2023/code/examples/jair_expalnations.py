from pyexplain.explain.parallel_greedy_incr_naive_explain import ParallelGreedyIncrNaiveExplain
from pyexplain.explain.greedy_explain import GreedyExplain
from pyexplain.explain.ocus_non_incr_explain import OCUSExplainNotIncremental
from pyexplain.explain.greedy_incr_naive_explain import GreedyIncrNaiveExplain
from pyexplain.solvers.params import COusNonIncrParams, COusParams, DisjointMCSes, Grow, Interpretation, OUSParallelIncrNaiveParams, OusIncrNaiveParams, OusParams, Weighing
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.utils.utils import cost_puzzle
from pysat.formula import CNF

from cppy import cnf_to_pysat

from cppy import *
from cppy.model_tools.to_cnf import *


#%% Problem building!
# Initialisation of the problem variables

# Pretty Printing of the explanations
# matching_table = {
#     -1: "~c1", -2: "~c_2", -3: "~c_3", -4: "~c_4",
#     1: "c_1", 2: "c_2", 3: "c_3", 4: "c_4",
#     5: "c_5", 6: "c_9", 7:"c_7",
#     -5: "c_8", -6: "c_6", -7:"c_{{10}}"
# }
# (b1, b2, b3, b4) = cppy_indicator_lits = BoolVar(4)
# (mayo, andalouse, ketchup) = cppy_user_vars = BoolVar(3)

(mayo, andalouse, ketchup) = cppy_user_vars = BoolVar(3)
(b1, b2, b3, b4) = cppy_indicator_lits = BoolVar(4)

# Building of the problem constraints 
c0 = ~b1 | ~mayo | ~andalouse | ketchup
c1 = ~b2 | ~mayo | andalouse | ketchup
c2 = ~b3 | mayo
c3 = ~b4 |  ~andalouse | ~ketchup

# F formula in CNF format
all_constraints = cnf_to_pysat([c0, c1, c2, c3])

# User variables: selected variables relevant to the user
user_vars = set([li.name+1 for li in cppy_user_vars]) | set([li.name+1 for li in cppy_indicator_lits])

# Indicator literals for activating and recognising constraints selected
I0 = indicator_lits = set([(li.name+1) for li in cppy_indicator_lits])

# BAse knowledge
known = set()
# known = set({mayo.name+1})

# Initial interpretation
I = I0 | known

# Clause weights according to paper
weights = {
    -(b1.name+1): 60, (b1.name+1): 60,
    -(b2.name+1): 60, (b2.name+1): 60,
    -(b3.name+1): 100, (b3.name+1): 100,
    -(b4.name+1): 100, (b4.name+1): 100
}

print("Initial information")
print("-------------------")
print("\tcnf          = {}\n\t\tall constraints\n".format(all_constraints))
print("\tI0           = {}\n\t\tIndicator literals for activating and recognising constraints selected\n".format(I0))
print("\tknown        = {}\n\t\tKnown information\n".format(known))
print("\tI (I0|known) = {}\n\t\tInitial interpretation\n".format(I))
print("\tweights      = {}\n\t\tClause weights".format(weights))
print("\tuser_vars     = {}\n\t\tClause weights".format(user_vars))

matching_table = {
    -4: "~c1", -5: "~c2", -6: "~c3", -7: "~c4",
    4: "c1", 5: "c2", 6: "c3", 7: "c4",
    1: "x1", 2: "x2", 3:"x3",
    -1: "~x1", -2: "~x2", -3:"~x3"
}

f = cost_puzzle(user_vars, I, weights)

# config_params = COusParams()
# config_params.instance = "simple"
# config_params.output = "simple_explanations.json"

# config_params.grow = Grow.CONSTRAINT_DISJ_MCS
# config_params.disjoint_mcs_interpretation = Interpretation.ACTUAL
# config_params.disjoint_mcs_weighing = Weighing.UNIFORM

# ocus_expl_computer = OCUSExplain(C=CNF(from_clauses=all_constraints), params=config_params, matching_table=matching_table, verbose=3)
# expl_sequence = ocus_expl_computer.explain(U=user_vars, f=f, I0=I)


config_params = OUSParallelIncrNaiveParams()
config_params.instance = "simple"
config_params.output = "simple_explanations.json"

config_params.grow = Grow.DISJ_MCS
config_params.disjoint_mcs_interpretation = Interpretation.ACTUAL
config_params.disjoint_mcs_weighing = Weighing.UNIFORM

ocus_expl_computer = ParallelGreedyIncrNaiveExplain(C=CNF(from_clauses=all_constraints), params=config_params, matching_table=matching_table, verbose=3)
expl_sequence = ocus_expl_computer.explain(U=user_vars, f=f, I0=I)



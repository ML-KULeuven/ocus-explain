from pyexplain.solvers.params import COusParams
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.utils.utils import cost_puzzle
from pysat.formula import CNF

from cppy import cnf_to_pysat

from cppy import *
from cppy.model_tools.to_cnf import *


#%% Problem building!
# Initialisation of the problem variables
(mayo, ketchup, andalouse) = cppy_user_vars = BoolVar(3)
(b1, b2, b3, b4) = cppy_indicator_lits = BoolVar(4)

# Building of the problem constraints 
c0 = ~b1 | ~mayo | ~andalouse | ketchup
c1 = ~b2 | ~mayo | andalouse | ketchup
c2 = ~b3 | mayo
c3 = ~b4 |  ~ketchup | ~andalouse

# F formula in CNF format
all_constraints = cnf_to_pysat([c0, c1, c2, c3])

# User variables: selected variables relevant to the user
user_vars = set([li.name+1 for li in cppy_user_vars]) | set([li.name+1 for li in cppy_indicator_lits])

# Indicator literals for activating and recognising constraints selected
I0 = indicator_lits = set([(li.name+1) for li in cppy_indicator_lits])

# BAse knowledge
known = set({mayo.name+1})

# Initial interpretation
I = I0 | known

# Clause weights according to paper
weights = {
    -(b1.name+1): 60,
    -(b2.name+1): 60,
    -(b3.name+1): 100,
    -(b4.name+1): 100
}

print("Initial information")
print("-------------------")
print("\tcnf          = {}\n\t\tall constraints\n".format(all_constraints))
print("\tI0           = {}\n\t\tIndicator literals for activating and recognising constraints selected\n".format(I0))
print("\tknown        = {}\n\t\tKnown information\n".format(known))
print("\tI (I0|known) = {}\n\t\tInitial interpretation\n".format(I))
print("\tweights      = {}\n\t\tClause weights".format(weights))

# Pretty Printing of the explanations
matching_table = {
    4: "~c1", 5: "~c2", 6: "~c3", 7: "~c4",
    -4: "c1", -5: "c2", -6: "c3", -7: "~c4",
    1: "x1", 2: "x2", 3:"x3",
    -1: "~x1", -2: "~x2", -3:"~x3"
}

f = cost_puzzle(user_vars, I, weights)

config_params = COusParams()

ocus_expl_computer = OCUSExplain(C=CNF(from_clauses=all_constraints), params=config_params, matching_table=matching_table, verbose=True)
ocus_expl_computer.explain(U=user_vars, f=f, I0=I)

# PUZZLE_FUNS = {"simple": simpleProblem}

# ALL_EXPLANATION_COMPUTERS = {
#     "OCUS+Incr. HS": (COusParams(), OCUSExplain),
#     "OCUS": (COusNonIncrParams(), OCUSExplainNotIncremental),
#     "OUS+SS. caching": (OusParams(), GreedyExplain),
#     "OUS+Lit. Incr. HS":(OusIncrNaiveParams(), GreedyIncrNaiveExplain),
#     "OUS":(OusParams(reuse_SSes=False), GreedyExplain),
#     "MUS": (MUSParams(), MUSExplain)
# }

# ## CONSTRAINED OUS + INCREMENTAL - automatically loads
# ## best configuration for running puzzle
# params, explanation_computer = ALL_EXPLANATION_COMPUTERS[CONFIG]

# puzzleFun = PUZZLE_FUNS[INSTANCE]

# # getting the clauses and weights
# p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()

# # transform to CNF object
# o_cnf = CNF(from_clauses=p_clauses)

# # User vocabulary
# U = p_user_vars | set(x for lst in p_ass for x in lst)

# # initial interpretation
# I = set(x for lst in p_ass for x in lst)

# # weight/cost of explanations
# f = cost_puzzle(U, I, p_weights)

# ocus_expl_computer = explanation_computer(C=o_cnf, params=params, matching_table=matching_table, verbose=True)
# ocus_expl_computer.explain(U=U, f=f, I0=I)



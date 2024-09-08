from pyexplain.explain.parallel_greedy_incr_naive_explain import ParallelGreedyIncrNaiveExplain
from pyexplain.solvers.params import COusParams, DisjointMCSes, Grow, Interpretation, OUSParallelIncrNaiveParams, Weighing
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.utils.utils import cost_puzzle
from pysat.formula import CNF

from cppy import cnf_to_pysat

from cppy import *
from cppy.model_tools.to_cnf import *


#%% Problem building!
# Initialisation of the problem variables
(mayo, ketchup, curry, andalouse, samurai) = cppy_user_vars = BoolVar(5)
(b1, b2, b3, b4, b5, b6, b7, b8, b9, b10) = cppy_indicator_lits = BoolVar(10)

# Building of the problem constraints 

Nora =  mayo | ketchup
Leander = ~samurai | mayo
Benjamin = ~andalouse | ~curry | ~samurai
Behrouz = ketchup | curry | andalouse
Guy = ~ketchup | curry | andalouse
Daan = ~ketchup | ~curry | andalouse
Celine = ~samurai
Anton = mayo | ~curry | ~andalouse
Danny = ~mayo | ketchup | andalouse | samurai
Luc = ~mayo | samurai


allwishes = [Nora, Leander, Benjamin, Behrouz, Guy, Daan, Celine, Anton, Danny, Luc]
all_constraints = cnf_to_pysat(allwishes)

for id, ci in enumerate(all_constraints):
    s = []
    for c in ci:
        if c < 0:
            s.append("\\lnot x_{"+str(abs(c))+"}")
        else:
            s.append("x_{"+str(c)+"}")
    print("c_{" + str(id+1) + "}:=" + " \\vee ".join(s) + " \\qquad ")

Nora =  ~b1 |mayo | ketchup
Leander = ~b2 | ~samurai | mayo
Benjamin = ~b3 | ~andalouse | ~curry | ~samurai
Behrouz = ~b4 | ketchup | curry | andalouse
Guy = ~b5 | ~ketchup | curry | andalouse
Daan = ~b6 | ~ketchup | ~curry | andalouse
Celine = ~b7 | ~samurai
Anton = ~b8 | mayo | ~curry | ~andalouse
Danny = ~b9 | ~mayo | ketchup | andalouse | samurai
Luc = ~b10 | ~mayo | samurai


allwishes = [Nora, Leander, Benjamin, Behrouz, Guy, Daan, Celine, Anton, Danny, Luc]

# F formula in CNF format
all_constraints = cnf_to_pysat(allwishes)
print(all_constraints)

# User variables: selected variables relevant to the user
user_vars = set([li.name+1 for li in cppy_user_vars]) | set([li.name+1 for li in cppy_indicator_lits])

# Indicator literals for activating and recognising constraints selected
I0 = indicator_lits = set([(li.name+1) for li in cppy_indicator_lits])

# BAse knowledge
known = set()
# known = set({mayo.name+1})

# Initial interpretation
I = I0 | known

# Pretty Printing of the explanations
matching_table = {
    1: "mayo", 2: "ketchup", 3:"curry", 4: "andalouse", 5: "samurai",
    -1: "~mayo", -2: "~ketchup", -3:"~curry", -4: "~andalouse", -5: "~samurai",
}

# Clause weights according to paper
weights = {}
for id, ind_var in enumerate(cppy_indicator_lits):
    clause_weight = 60

    if id%2 != 0:
        clause_weight = 100

    weights[ind_var.name+1] = clause_weight
    weights[-(ind_var.name+1)] = clause_weight

    matching_table[ind_var.name+1] = "c"+str(id+1)
    matching_table[-(ind_var.name+1)] = "~c"+str(id+1)

print("Initial information")
print("-------------------")
print("\tcnf          = {}\n\t\tall constraints\n".format(all_constraints))
print("\tI0           = {}\n\t\tIndicator literals for activating and recognising constraints selected\n".format(I0))
print("\tknown        = {}\n\t\tKnown information\n".format(known))
print("\tI (I0|known) = {}\n\t\tInitial interpretation\n".format(I))
print("\tweights      = {}\n\t\tClause weights".format(weights))


f = cost_puzzle(user_vars, I, weights)

config_params = COusParams()
config_params.instance = "simple"
config_params.output = "simple_explanations.json"
config_params.grow = Grow.SUBSETMAX
config_params.disjoint_mcs_interpretation = Interpretation.ACTUAL
config_params.disjoint_mcs_weighing = Weighing.UNIFORM

ocus_expl_computer = OCUSExplain(C=CNF(from_clauses=all_constraints), params=config_params, matching_table=matching_table, verbose=2)
expl_sequence = ocus_expl_computer.explain(U=user_vars, f=f, I0=I)

print("--------------------------------------------------------------")


# config_params = COusParams()
# config_params.instance = "simple"
# config_params.output = "simple_explanations.json"
# config_params.grow = Grow.DISJ_MCS
# config_params.disjoint_mcs_interpretation = Interpretation.ACTUAL
# config_params.disjoint_mcs_weighing = Weighing.UNIFORM

# ocus_expl_computer = OCUSExplain(C=CNF(from_clauses=all_constraints), params=config_params, matching_table=matching_table, verbose=3)
# expl_sequence = ocus_expl_computer.explain(U=user_vars, f=f, I0=I)
# print("WHole sequence:\n", expl_sequence)

# ## Computing next best explanation given current interpretation
# expl_1_step = ocus_expl_computer.explain_1_step(U=user_vars, f=f, I0=I)
# print("Explain 1 step:\n", expl_1_step)

# ## Computing best explanation for given literal
# expl_1_lit = ocus_expl_computer.explain_1_lit(f=f, lit=2, I0=I)
# print("Explain 1 literal:\n", expl_1_lit)

# ocus_expl_computer.export_statistics(config_params, fname="output.json")

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



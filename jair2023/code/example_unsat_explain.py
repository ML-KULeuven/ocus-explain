from unsat_explain.explain.ocus_not_incr_explain_unsat import OCUSUnsatExplain
from unsat_explain.solvers.params import UNSATCOusNonIncrParams, UNSATExplanationComputer
from unsat_explain.examples.instances import smus_assumptions
from pysat.formula import CNF
# unit cost-function
f = lambda x: 1

d_smus_assumptions = smus_assumptions()

clauses = d_smus_assumptions['clauses']
cnf = CNF(from_clauses=clauses)
user_vars = d_smus_assumptions['vars']
assumptions = d_smus_assumptions['assumptions']
matching_table= d_smus_assumptions['matching_table']

params = UNSATCOusNonIncrParams()
explainer = OCUSUnsatExplain(C=cnf, params=params, matching_table=matching_table, verbose=3)
# explainer.unsat_explain_1_step(f=f, U=user_vars, assumptions=assumptions, I0=set())
explainer.unsat_explain(f=f, U=user_vars, assumptions=assumptions, I0=set())
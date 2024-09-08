import random
from pyexplain.utils.utils import get_expl
from unsat_explain.examples.instances import smus_assumptions
from pysat.formula import CNF
from pysat.solvers import Solver

## gurobi
import gurobipy as gp
from gurobipy import GRB

# unit cost-function
f = lambda x: 1

class HittingSetSolver():
    def __init__(self, F):
        self.allLits = list(F)
        nAllLits = len(self.allLits)

        # optimisation model
        self.opt_model = gp.Model('OptHittingSet')
        self.opt_model.Params.OutputFlag = 0
        self.opt_model.Params.LogToConsole = 0
        self.opt_model.Params.Threads = 1

        # VARIABLE -- OBJECTIVE
        x = self.opt_model.addMVar(
            shape=nAllLits,
            vtype=GRB.BINARY,
            obj=[1]* nAllLits,
            name="x")

        self.opt_model.update()

    def addCorrectionSet(self, C: set):
        """Add new constraint of the form to the optimization model,
        mapped back to decision variable lit => x[i].

            sum x[j] * hij >= 1

        Args:
            C (set): set of assumption literals.
        """
        x = self.opt_model.getVars()

        Ci = [self.allLits.index(lit) for lit in C]

        # add new constraint sum x[j] * hij >= 1
        self.opt_model.addConstr(gp.quicksum(x[i] for i in Ci) >= 1)

    def OptHittingSet(self):
        """Compute conditional Optimal hitting set.

        Returns:
            set: Conditional optimal hitting mapped to assumption literals.
        """
        self.opt_model.optimize()
        x = self.opt_model.getVars()
        hs = set(lit for i, lit in enumerate(self.allLits) if x[i].x == 1)
        return hs

def improve_model(sat_solver, F, model):
    sat = True
    F_list = list(F)
    random.shuffle(F_list)
    F_iter = iter(F_list)
    while(sat):
        ci = next(F_iter)
        sat = sat_solver.solve(model | set({ci}))
        if sat:
            model |= set({ci})
    return model

def SMUS(clauses, assumptions, matching_table, improve=False):
    F = set(assumptions)
    sat_solver = Solver(bootstrap_with=clauses)
    hittingset_solver = HittingSetSolver(F)
    # print("")
    while(True):
        hs = hittingset_solver.OptHittingSet()

        sat = sat_solver.solve(assumptions=hs)
        if not sat:
            print(f"${get_expl(matching_table, hs)}$ & {sat} & & ")
            return hs

        model = set(sat_solver.get_model())
        if improve:
            model = improve_model(sat_solver, F, model&F)

        C = F - model
        print(f"${get_expl(matching_table, hs)}$ & {sat} & $\\{{{get_expl(matching_table, F&model)}\\}}$\t&$\\{{{get_expl(matching_table, C)}\\}}$ \\\\")
        hittingset_solver.addCorrectionSet(C)


if __name__ == '__main__':
    ## instance generation
    d_smus_assumptions = smus_assumptions()

    clauses = d_smus_assumptions['clauses']
    assumptions = d_smus_assumptions['assumptions']
    matching_table = d_smus_assumptions["matching_table"]
    print(SMUS(clauses, assumptions, matching_table))

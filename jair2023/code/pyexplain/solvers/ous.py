from .hittingSet import OptHS
from pysat.solvers import Solver

class OUS:
    """
    Class for computing the cost-Optimal Unsatisfiable subset of a given
    formula in CNF. The optimality criterion is related to the weights
    of soft clauses i.e, given assumptions.

    """


    def __init__(self, cnf, weights) -> None:
        """
            OUS 

        """
        # initalisation
        self.OPTHSSolver = None
        self.SATSolver = None

        # apply pre-processing techniques
        clauses = self.preprocessing(cnf, weights)
        assumption_literals = 

        # TODO: build the full assumptions
        self.full = set(assumption_literals)

        # build optimal hitting set solver
        self.buildHSSolver(clauses, weights)
        self.buildSATSolver(clauses)

    def add_assumption(self, bi):
        self.full |= set(bi)

    def add_clause(self, clause, weight=None):

        new_clause = list(clause)
        bi = self.new_assumption_lit()

        self.SATSolver.add_clause(new_clause)
        if bi:
            self.add_assumption([bi])
        return bi

    def new_assumption_lit(self):
        # TODO: check this is correct in POSTOPT paper
        bi = max(self.full) + 1
        return -bi

    def extend(self, clauses, weights=None):

        if weights:
            new_clauses = list(clauses)
            self.SATSolver.append_formula(new_clauses)
        else:
            self.SATSolver.append_formula(clauses)

    def preprocessing(self, cnf, weights):
        clauses = []
        return clauses

    def buildSATSolver(self, clauses):
        self.SATSolver = Solver(bootstrap_with=clauses)

    def buildHSSolver(self, clauses, weights):
        self.OPTHSSolver = OptHS(clauses, weights)

    def grow(self, hs):
        return 

    def __del__(self):
        if self.SATSolver:
            self.SATSolver.delete()
        if self.OPTHSSolver:
            self.OPTHSSolver.delete()

    def solve(self):
        """

        input:

        output:
        - subset of clauses unsatisfiable together and optimal with respect
        to optimality criterion
        """
        F = self.full

        while(True):
            hs = self.OPTHSSolver.OptHittingSet()

            sat = self.SATSolver.solve(assumptions=hs)

            if not sat:
                return hs

            C = F - hs
            self.OPTHSSolver.addCorrectionSet(C)

    def postprocessing(self):
        pass

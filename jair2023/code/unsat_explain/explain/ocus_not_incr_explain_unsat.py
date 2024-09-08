from unsat_explain.explain.explain_unsat import CSPUnsatExplain
from pyexplain.utils.utils import get_expl
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import UNSATCondOptHS

class OCUSUnsatExplain(CSPUnsatExplain, BestStepComputer):
    def __init__(self, C, params, verbose=True, matching_table=None):
        self.verbose = verbose
        CSPUnsatExplain.__init__(self, C=C, verbose=verbose,matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat, params=params)


    def bestStep(self, f, Iend: set, I: set):
        self.Iend = set(Iend)
        self.I = set(I)

        F = I | set(-l for l in Iend - I)

        if self.verbose > 2:
            print(f"\t{I=}")
            print(f"\t{Iend=}")
            print(f"\t{F=}")

        hittingset_solver = UNSATCondOptHS(Iend=Iend, I=I)
        hittingset_solver.updateObjective(f, F)

        while(True):

            # COMPUTING OPTIMAL HITTING SET
            HS = hittingset_solver.CondOptHittingSet()

            if self.verbose > 2:
                print("\n\tHS\t= ", get_expl(self.matching_table, HS), f"({HS})")

            # CHECKING SATISFIABILITY
            sat, HS_model = self.checkSat(HS)

            if self.verbose > 2:
                print("\n\tsat model \t= ", get_expl(self.matching_table, HS_model&self.U))

            # OCUS FOUND?
            if not sat:
                return HS

            C = F - (HS_model)
            if self.verbose > 2:
                print("\n\tCorr: \t= ", get_expl(self.matching_table, C))
            hittingset_solver.addCorrectionSet(C)

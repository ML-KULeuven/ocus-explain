from pyexplain.solvers.hittingSet import CondOptHS
from pyexplain.utils.utils import get_expl
from pyexplain.solvers.bestStep import BestStepComputer, optimalPropagate

class OCUSIncrementalUnsatExplain(BestStepComputer):
    def __init__(self, C, params, sat, verbose=True):
        BestStepComputer.__init__(self, cnf=C, sat=sat, params=params)
        
    def preprocess(self, U, f, I0, Iend):
        self.hittingset_solver = CondOptHS(Iend=Iend, I=I0)
        
    def bestStep(self, f, Iend, I):

        F = set(l for l in Iend)
        F |= set(-l for l in Iend)
        F -= set(-l for l in I)
        
        F_explain = set(l for l in Iend)
        F_explain |= set(-l for l in Iend)
        F_explain -= set(l for l in I)
        F_explain -= set(-l for l in I)

        return self.bestStepCOUS(f, F, F_explain)
    
    def bestStepCOUS(self, f, F, F_explain):
        if self.verbose > 2:
            print("A=", F_explain)
            print("F=", F)
        
        # UPDATE OBJECTIVE WEIGHTS
        self.hittingset_solver.updateObjective(f, F_explain)

        while(True):

            # COMPUTING OPTIMAL HITTING SET
            HS = self.hittingset_solver.CondOptHittingSet()

            if self.verbose > 1:
                print("\nHS\t= ", get_expl(self.matching_table, HS), f"({HS})")

            # CHECKING SATISFIABILITY
            sat, HS_model = self.checkSat(HS, phases=self.Iend)

            if self.verbose > 2:
                print("\sat model \t= ", get_expl(self.matching_table, HS_model), f"(phases={self.Iend})")

            # OUS FOUND?
            if not sat:
                return HS

            C = F - HS_model
            self.hittingset_solver.addCorrectionSet(C)

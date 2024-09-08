from pyexplain.utils.utils import get_expl
from pyexplain.explain.ocus_explain import OCUSExplain
import time
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import CondOptHS
from pysat.formula import CNF
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.solvers.params import COusNonIncrHSParams, DisjointMCSes


class OCUSExplainNotIncrementalHS(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: COusNonIncrHSParams, verbose=False, matching_table=None):
        assert isinstance(params, COusNonIncrHSParams), f"Expected {COusNonIncrHSParams} got {type(params)}"
        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

        self.time_statisitics.update({
            "opt": [],
            "sat": [],
            "grow": [],
            "disj_mcs": [],
            "remaining": []
        })

        self.call_statistics.update({
            "#opt": [],
            "#sat": [],
            "#grow": [],
            "#disj_mcs": [],
            "#hs": [],
            "#hs_disj_mcs": [],
        })
    def preprocess(self, U: set, f, I0: set, Iend, end_time_timeout=None):
        CSPExplain.preprocess(self, U, f, I0, Iend)
        # initial values

    def bestStep(self, f, Iend: set, I: set, end_time_timeout=None):
        """
        bestStep computes a subset A' of A that satisfies p s.t.
        C u A' is UNSAT and A' is f-optimal.

        Args:

            f (list): A cost function mapping 2^A -> N.
            Iend (set): The cautious consequence, the set of literals that hold in
                        all models.
            I (set): A partial interpretation such that I \subseteq Iend.
            sat (pysat.Solver): A SAT solver initialized with a CNF.
        """
        t_mip = 0

        Iexpl = Iend - I

        A = I | set(-l for l in Iexpl)
        sat, _ = self.checkSat(A)
        assert not sat, "Formula should not be satisfiable"

        ### Given a set of assumption literals A subset of F, bestStepCOUS
        ### computes a subset a subset A' of A that satisfies p s.t C u A' is
        ### UNSAT and A' is f-optimal based on [1].
        # Args:
        #     f (func): Cost function mapping from lit to int.
        #     F (set): Set of literals I + (Iend \\ I)) + (-Iend \\ -I).
        #     A (set): Set of assumption literals I + (-Iend \\ -I).
        # Returns:
        #     set: a subset A' of A that satisfies p s.t C u A' is UNSAT
        #          and A' is f-optimal.
        t_mip = 0

        if self.verbose > 2:
            print("A=", A)

        # UPDATE OBJECTIVE WEIGHTS
        sets_to_hit = []

        while(True):

            tmip = time.time()
            # INITIALIZE
            # COMPUTING OPTIMAL HITTING SET
            hittingset_solver = CondOptHS(Iend=Iend, I=I)
            hittingset_solver.updateObjective(f, A)
            hittingset_solver.addCorrectionSets(sets_to_hit)
            HS = hittingset_solver.CondOptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)

            if self.verbose > 1:
                print("\nHS\t= ", get_expl(self.matching_table, HS), f"({HS})")

            # CHECKING SATISFIABILITY
            sat, HS_model = self.checkSat(HS, phases=self.Iend)
            if self.verbose > 2:
                print("\sat model \t= ", get_expl(self.matching_table, HS_model), f"(phases={self.Iend})")

            # OUS FOUND?
            if not sat:
                if self.verbose > 1:
                    print("\nOCUS\t= ", get_expl(self.matching_table, HS), f"({HS})")
                # call statistics
                self.time_statisitics["opt"].append(t_mip)

                return HS

            to_hit = self.grow(F=A, f=f, A=A, HS=HS, HS_model=HS_model, end_time_timeout=end_time_timeout)
            sets_to_hit += to_hit

            if self.verbose > 1:
                for hs in to_hit:
                    print("Unit -MCS \t= ", get_expl(self.matching_table, hs))


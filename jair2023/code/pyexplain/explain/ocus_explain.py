from pyexplain.utils.utils import get_expl
import time
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import CondOptHS
from pysat.formula import CNF
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.solvers.params import COusNonIncrParams, COusParams, DisjointMCSes, Grow


class OCUSExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: COusParams, verbose=True, matching_table=None):
        assert isinstance(params, (COusParams, COusNonIncrParams)), f"Expected {COusParams} got {type(params)}"
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
        t_mip = 0

        # initialise data structures for tracking of information
        CSPExplain.preprocess(self, U, f, I0, Iend, end_time_timeout)

        if self.verbose > 1:
            print("Iend=", self.Iend)

        tmip = time.time()
        self.hittingset_solver = CondOptHS(Iend=Iend, I=I0)
        t_mip+= (time.time() - tmip)

        Iexpl = Iend - I0
        F = set(l for l in Iend) | set(-l for l in Iend)
        F -= set(-l for l in I0)

        A = I0 | set(-l for l in Iexpl)

        self.time_statisitics["opt"].append(t_mip)

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
        self.I = set(I)

        Iexpl = Iend - I

        F = set(l for l in Iend) | set(-l for l in Iend)

        F -= set(-l for l in I)

        A = I | set(-l for l in Iexpl)
        if self.verbose > 2:
            print("Bestep- A=", A)
            print("Bestep- F=", F)

        return self.bestStepCOUS(f, F, A, end_time_timeout)

    def bestStepCOUS(self, f, F, A: set, end_time_timeout=None):
        """Given a set of assumption literals A subset of F, bestStepCOUS
        computes a subset a subset A' of A that satisfies p s.t C u A' is
        UNSAT and A' is f-optimal based on [1].

        Args:
            f (func): Cost function mapping from lit to int.
            F (set): Set of literals I + (Iend \\ I)) + (-Iend \\ -I).
            A (set): Set of assumption literals I + (-Iend \\ -I).

        Returns:
            set: a subset A' of A that satisfies p s.t C u A' is UNSAT
                 and A' is f-optimal.
        """
        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs = 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0

        if self.verbose > 2:
            print("A=", A)
            print("F=", F)

        # UPDATE OBJECTIVE WEIGHTS
        tmip = time.time()
        self.hittingset_solver.updateObjective(f, A)
        t_mip+= (time.time() - tmip)

        while(True):

            # COMPUTING OPTIMAL HITTING SET
            tmip = time.time()
            HS = self.hittingset_solver.CondOptHittingSet(end_time_timeout)
            t_mip+= (time.time() - tmip)
            n_opt += 1

            if self.verbose > 1:
                print("\nHS\t= ", get_expl(self.matching_table, HS), f"({HS})")

            # CHECKING SATISFIABILITY
            tsat = time.time()
            sat, HS_model = self.checkSat(HS, phases=self.Iend)
            t_sat += (time.time() - tsat)
            n_sat +=1
            if self.verbose > 2:
                print("\sat model \t= ", get_expl(self.matching_table, HS_model), f"(phases={self.Iend})")

            # OUS FOUND?
            if not sat:
                if self.verbose > 1:
                    print("\nOCUS\t= ", get_expl(self.matching_table, HS), f"({HS})")
                # call statistics
                self.time_statisitics["opt"].append(t_mip)
                self.time_statisitics["sat"].append(t_sat)
                self.time_statisitics["grow"].append(t_grow)
                self.time_statisitics["disj_mcs"].append(t_disj_mcs)

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)
                return HS

            tgrow = time.time()
            to_hit = self.grow(F=F, f=f, A=A, HS=HS, HS_model=HS_model, end_time_timeout=end_time_timeout)
            t_grow += (time.time() - tgrow)
            n_grow +=1
            n_hs +=len(to_hit)
            
            tmip = time.time()
            self.hittingset_solver.addCorrectionSets(to_hit)
            t_mip += (time.time() - tmip)
        
            if self.verbose > 1:
                for hs in to_hit:
                    print("Unit -MCS \t= ", get_expl(self.matching_table, hs))

    def __del__(self):
        """Ensure sat solver is deleted after garbage collection.
        """
        if hasattr(self,"hittingset_solver") and self.hittingset_solver is not None:
            self.hittingset_solver.__del__()

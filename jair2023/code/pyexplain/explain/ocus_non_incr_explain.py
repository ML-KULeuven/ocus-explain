from pyexplain.utils.utils import get_expl
from pyexplain.explain.ocus_explain import OCUSExplain
import time
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import CondOptHS
from pysat.formula import CNF
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.solvers.params import COusNonIncrParams, DisjointMCSes


class OCUSExplainNotIncremental(OCUSExplain, BestStepComputer):
    def __init__(self, C: CNF, params: COusNonIncrParams, verbose=False, matching_table=None):
        assert isinstance(params, COusNonIncrParams), f"Expected {COusNonIncrParams} got {type(params)}"
        OCUSExplain.__init__(self, C=C, params=params, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

    def preprocess(self, U: set, f, I0: set, Iend, end_time_timeout=None):
        CSPExplain.preprocess(self, U, f, I0, Iend)
        # initial values
        self.hittingset_solver = None

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
        self.I = set(I)

        Iexpl = Iend - I

        A = I | set(-l for l in Iexpl)
        sat, _ = self.checkSat(A)
        assert not sat, "Formula should not be satisfiable"

        tmip = time.time()
        self.hittingset_solver = CondOptHS(Iend=Iend, I=self.I)
        t_mip+= (time.time() - tmip)

        self.time_statisitics["opt"].append(t_mip)

        cOUS = self.bestStepCOUS(f, A, A, end_time_timeout)

        self.hittingset_solver.delete()
        return cOUS

import time
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import OptHS
from pysat.formula import CNF
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.solvers.params import BestStepParams, DisjointMCSes, Grow, OusNoOptParams
from pyexplain.utils.utils import get_expl


class GreedyNoOptExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: BestStepParams, verbose=False, matching_table=None):
        assert isinstance(params, OusNoOptParams), f"Expected {OusNoOptParams} got {type(params)}"
        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

        self.time_statisitics.update({
            "opt": [],
            "sat": [],
            # grow with disj.mcs or maxsat
            "grow": [],
            "disj_mcs": [],
            # bootstrapping with disjoint mcs enumeration
            "preseeding": [],
            "postprocessing": [],
            "remaining": []
        })

        self.call_statistics.update({
            "#opt": [], # number of calls to otpimsiation solver
            "#sat": [], # number of calls to sat solver
            "#grow": [], # number of calls to grow
            "#hs": [], # number of sets to hit computed
            "#hs_disj_mcs": [], # number of sets to hit computed with disj. mcs. enumeration
            "#disj_mcs": [],
            "#SSes_before":[],
            "#SSes_after":[]
        })

    def preprocess(self, U:set, f, I0: set, Iend: set, end_time_timeout=None):
        # initialise data structures for tracking of information
        CSPExplain.preprocess(self, U, f, I0, Iend)
        self.SSes = set()
        # end-interperation
        self.fullSS = set(Iend)

    def bestStep(self, f, Iend, I: set, end_time_timeout=None):
        best_expl, best_cost = None, sum(f(l) for l in Iend)
        self.I = set(I)

        # best cost
        remaining = list(Iend - I)

        for id, l in enumerate(remaining):
            # expl is None when cutoff (timeout or cost exceeds current best Cost)
            A = I | set({-l})

            expl, cost_expl = self.ous(f, F=A, A=A, lit=set({-l}), end_time_timeout=end_time_timeout)

            # store explanation
            if cost_expl <= best_cost:
                best_expl = expl
                best_cost = cost_expl

        return best_expl

    def process_SSes(self, H):
        self.SSes |= H
        self.call_statistics["SSes_before"].append(len(self.SSes))
        self.SSes = set(x for x in self.SSes if not any(x<=y for y in self.SSes if x is not y))

        # post-processing the MSSes
        self.call_statistics["SSes_after"].append(len(self.SSes))

    def ous(self, f, F, A, lit=None, end_time_timeout=None):
        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs, t_preseed, t_post_processing = 0, 0, 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0

        HS, C, SSes = set(), set(), set()

        # OPTIMISATION MODEL
        tmip = time.time()
        hittingset_solver = OptHS(f, F, A)
        hittingset_solver.addCorrectionSet(lit)
        t_mip += (time.time() - tmip)

        # lit to explain!
        tpreseed = time.time()

        if self.params.reuse_SSes:
            for SS in self.SSes:
                ss = SS & F

                if len(ss) == 0:
                    continue

                C = F - ss
                tmip = time.time()
                hittingset_solver.addCorrectionSet(C)
                t_mip += (time.time() - tmip)
                n_hs +=1

        t_preseed += (time.time() - tpreseed)

        while(True):
            tmip = time.time()
            HS = hittingset_solver.OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt +=1

            tsat = time.time()
            sat, HSModel = self.checkSat(HS, phases=self.Iend)
            t_sat += (time.time() -tsat)
            n_sat += 1

            costHS = sum(f(l) for l in HS)

            # OUS FOUND?
            if not sat:
                # cleaning up!
                hittingset_solver.dispose()

                #postprocessing
                if self.params.reuse_SSes:
                    tpost = time.time()
                    self.process_SSes(SSes)
                    t_post_processing += (time.time() - tpost)

                # call statistics
                self.time_statisitics["opt"].append(t_mip)
                self.time_statisitics["sat"].append(t_sat)
                self.time_statisitics["grow"].append(t_grow)
                self.time_statisitics["disj_mcs"].append(t_disj_mcs)
                self.time_statisitics["preseeding"].append(t_preseed)
                self.time_statisitics["postprocessing"].append(t_post_processing)

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)
                return HS, costHS

            tgrow = time.time()
            to_hit = self.grow(F=F, f=f, A=A, HS=HS, HS_model=HSModel, end_time_timeout=end_time_timeout)
            t_grow += (time.time() - tgrow)
            n_grow +=1
            n_hs +=len(to_hit)
            
            tmip = time.time()
            hittingset_solver.addCorrectionSets(to_hit)
            t_mip += (time.time() - tmip)
        
            if self.verbose > 1:
                for hs in to_hit:
                    print("Unit -MCS \t= ", get_expl(self.matching_table, hs))

            if self.params.reuse_SSes:
                for ci in to_hit:
                    SSes.add(frozenset(F - ci))

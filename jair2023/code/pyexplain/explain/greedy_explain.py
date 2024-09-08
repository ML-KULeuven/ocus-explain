from pyexplain.utils.utils import get_expl
import time
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import OptHS
from pysat.formula import CNF
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.solvers.params import BestStepParams, DisjointMCSes, Grow, OusParams


class GreedyExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: OusParams, verbose=False, matching_table=None):
        assert isinstance(params, OusParams), f"Expected {OusParams} got {type(params)}"
        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

        self.SSes = None

        self.lb = dict()
        self.ub = dict()

        # setup statistics here!
        self.time_statisitics.update({
            "opt": [],
            "sat": [],
            # grow with disj.mcs or maxsat
            "grow": [],
            # bootstrapping with disjoint mcs enumeration
            "disj_mcs": [],
            # time to postprocess the satisfiable subsets
            "postprocessing": [],
            # preseeding with satisfiable subsets
            "preseeding": [],
            "remaining": []
        })

        self.call_statistics.update({
            "#opt": [],
            "#sat": [],
            "#grow": [],
            "#hs": [],
            "#hs_disj_mcs": [],
            "#disj_mcs": [],
            "SSes_before":[],
            "SSes_after":[],
            "#skipped":[],
        })

    def preprocess(self, U:set, f, I0: set, Iend: set, end_time_timeout=None):
        # initialise data structures for tracking of information
        CSPExplain.preprocess(self, U, f, I0, Iend)

        self.SSes = set()

        # initialize costs
        Xbest = I0 | {-l for l in  Iend - I0}
        f_xbest = sum(f(l) for l in Xbest)

        # pre-compute the best cost
        for l in Iend - I0:
            # initialising the best cost
            self.lb[l] = 0
            self.ub[l] = f_xbest

    def bestStep(self, f, Iend: set, I: set, end_time_timeout=None):
        """Beststep returns the next best literal to explain given the
        cost function.

        Args:
            f (S): Cost function mapping a set to an integer value.
            Iend (set): End interpretation
            I (set): Partial interpretation (given/known information)

        Returns:
            set: Explanation of a literal (subset of constraints of and
                 negated constraint I + [-lit] that are unsatisfiable and
                 cost-optimal w.r.t to given cost function f)
        """
        t_best_step_start, t_ous = time.time(), 0
        skipped = 0

        self.I = set(I)

        # BEST EXPLANATION
        best_expl, best_lit = None, None

        # COST MANAGEMENT
        remaining = list(Iend - I)

        for lit in I.intersection(self.lb):
            del self.lb[lit]
            del self.ub[lit]

        if self.params.sort_literals:
            remaining.sort(key=lambda l: self.lb[l])

        best_cost = min(self.ub.values())

        for id, l in enumerate(remaining):
            if self.verbose > 1:
                print(f"OUS lit {id+1}/{len(remaining)+1}", flush=True, end='\r')

            # FORMULA to explain
            A = I | set({-l})

            tous = time.time()
            expl, cost_expl = self.ous(f, F=A, A=A, lit=set({-l}), end_time_timeout=end_time_timeout)
            t_ous += time.time() - tous

            self.lb[l] = cost_expl

            # expl is None when cutoff (timeout or cost exceeds current best Cost)
            if expl is None:
                skipped += 1
                continue

            self.ub[l] = cost_expl

            # store explanation
            if cost_expl <= best_cost:
                best_expl = expl
                best_lit = l
                best_cost = cost_expl

        # literal already found, remove its cost
        del self.ub[best_lit]
        del self.lb[best_lit]

        # updating statistics
        self.call_statistics["#skipped"].append(skipped)
        self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_ous)

        return best_expl

    def process_SSes(self, H):
        self.SSes |= H
        self.call_statistics["SSes_before"].append(len(self.SSes))
        self.SSes = set(x for x in self.SSes if not any(x<=y for y in self.SSes if x is not y))

        # post-processing the MSSes
        self.call_statistics["SSes_after"].append(len(self.SSes))

    def reuse_satisfiable_subsets(self, F):
        nHS = 0

        for SS in self.SSes:
            ss = SS & F

            if len(ss) == 0:
                continue

            C = F - ss

            self.hittingset_solver.addCorrectionSet(C)
            nHS+=1

        return nHS

    def ous(self, f, F, A, best_cost=None, lit=None, end_time_timeout=None):
        # initial running varaibles
        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs, t_preseed = 0, 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0

        HS, C, SSes = set(), set(), set()

        # initial best cost
        best_cost = min(self.ub.values())

        # OPTIMISATION MODEL
        tmip = time.time()
        self.hittingset_solver = OptHS(f, F, A)
        self.hittingset_solver.addCorrectionSet(lit)
        t_mip += (time.time() - tmip)

        if self.params.reuse_SSes:
            tpreseed = time.time()
            n_hs += self.reuse_satisfiable_subsets(F=F)
            t_preseed += (time.time() - tpreseed)

        while(True):

            # COMPUTING OPTIMAL HITTING SET
            tmip = time.time()
            HS = self.hittingset_solver.OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt +=1


            if self.verbose > 1:
                print("\nHS\t= ", get_expl(self.matching_table, HS), f"({HS})")


            tsat = time.time()
            # CHECKING SATISFIABILITY
            sat, HSModel = self.checkSat(HS, phases=self.Iend)
            t_sat += (time.time() -tsat)
            n_sat += 1

            costHS = sum(f(l) for l in HS)

            # OUS FOUND?
            if not sat:
                # call statistics
                self.time_statisitics["opt"].append(t_mip)
                self.time_statisitics["sat"].append(t_sat)
                self.time_statisitics["grow"].append(t_grow)
                self.time_statisitics["disj_mcs"].append(t_disj_mcs)
                self.time_statisitics["preseeding"].append(t_preseed)

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)

                # cleaning up!
                self.hittingset_solver.dispose()

                #postprocessing
                if self.params.reuse_SSes:
                    tpost = time.time()
                    self.process_SSes(SSes)
                    self.time_statisitics["postprocessing"].append(time.time() - tpost)

                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)
                return HS, costHS

            # cut the search if cost exceeds treshold
            if costHS > best_cost:
                # call statistics
                self.time_statisitics["opt"].append(t_mip)
                self.time_statisitics["sat"].append(t_sat)
                self.time_statisitics["grow"].append(t_grow)
                self.time_statisitics["disj_mcs"].append(t_disj_mcs)
                self.time_statisitics["preseeding"].append(t_preseed)

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)

                # cleaning up!
                self.hittingset_solver.dispose()

                #postprocessing
                if self.params.reuse_SSes:
                    tpost = time.time()
                    self.process_SSes(SSes)
                    self.time_statisitics["postprocessing"].append(time.time() - tpost)

                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)
                return None, costHS

            tgrow = time.time()
            to_hit = self.grow(F=F, f=f, A=A, HS=HS, HS_model=HSModel, end_time_timeout=end_time_timeout)
            t_grow += (time.time() - tgrow)
            n_grow +=1
            n_hs +=len(to_hit)
            
            tmip = time.time()
            self.hittingset_solver.addCorrectionSets(to_hit)
            t_mip += (time.time() - tmip)
        
            if self.verbose > 1:
                for hs in to_hit:
                    print("Unit -MCS \t= ", get_expl(self.matching_table, hs))

            if self.params.reuse_SSes:
                for ci in to_hit:
                    SSes.add(frozenset(F - ci))

from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.utils.utils import get_expl
import time
from pysat.formula import CNF
from pyexplain.solvers.params import DisjointMCSes, Grow, OUSParallelNaiveParams
from pyexplain.solvers.hittingSet import OptHS
import heapq as hq

class ParallelGreedyNaiveExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: OUSParallelNaiveParams, verbose=True, matching_table=None):
        assert isinstance(params, OUSParallelNaiveParams), f"Expected {OUSParallelNaiveParams} got {type(params)}"
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
            "remaining": []
        })

        self.call_statistics.update({
            "#opt": [], # number of calls to otpimsiation solver
            "#sat": [], # number of calls to sat solver
            "#grow": [], # number of calls to grow
            "#disj_mcs": [], # number of calls to disj. mcs
            "#hs": [], # number of sets to hit computed
            "#hs_disj_mcs": [], # number of sets to hit computed with disj. mcs. enumeration
            "#skipped": [] # literals explained skipped
        })

    def bestStep(self, f, Iend, I, increments=1, end_time_timeout=None):

        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs = 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0
        # keeping track of all solvers
        opt_solvers = {}

        # update interpretation
        self.I = set(I)

        # best cost
        remaining = list(Iend - I)
        # remove bounds on elements that are not in the remaining literals
        # to explain
        lb = []
        for lit in remaining:
            # Formula to explain
            A = I | set({-lit})

            # Fomula with reuse of satisfiable subsets
            F = I | set({-lit})
            if self.verbose > 2:
                print(f"\nl={get_expl(self.matching_table, [lit])}\t{F=}\t{A=}\n")
            mcses = [set({-lit})]

            # OPITMISATION MODEL
            tmip = time.time()
            opt_solvers[lit] = OptHS(f, F, I)
            opt_solvers[lit].updateObjective(f, A)
            opt_solvers[lit].addCorrectionSets(mcses)
            # computing a lower bound for every literal
            HS = opt_solvers[lit].OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt += 1

            # adding it to the heaaaap
            hq.heappush(lb, (sum(f(l) for l in HS), lit, HS))

        expl_found = False

        # keep Track of best explanation
        best_expl = None

        # initialising the best cost
        while(not expl_found):
            (_, lit, HS) = hq.heappop(lb)
            A = I | set({-lit})

            # not incremental => don't care about the literals not yet derived!
            F = I | set({-lit})

            if self.verbose > 2:
                print(f"\nlit={get_expl(self.matching_table, [lit])}\tHS={get_expl(self.matching_table, HS)}\t{F=}\t{A=}\n")

            # checking satisfiability only on the one with lowest cost
            tsat = time.time()
            sat, HS_model = self.checkSat(HS, phases=self.Iend)
            t_sat += (time.time() - tsat)
            n_sat +=1

            if not sat:
                expl_found = True
                best_expl = HS
                break

            tgrow = time.time()
            to_hit = self.grow(F=F, f=f, A=A, HS=HS, HS_model=HS_model, end_time_timeout=end_time_timeout)
            t_grow += (time.time() - tgrow)
            n_grow +=1
            n_hs +=len(to_hit)
            
            tmip = time.time()
            opt_solvers[lit].addCorrectionSets(to_hit)
            t_mip += (time.time() - tmip)
        
            # OPT Hitting SET
            tmip = time.time()
            HS = opt_solvers[lit].OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt += 1

            hq.heappush(lb, (sum(f(l) for l in HS), lit, HS))

        # delete optimisation model
        for s in opt_solvers.values():
            s.delete()

        self.time_statisitics["opt"].append(t_mip)
        self.time_statisitics["sat"].append(t_sat)
        self.time_statisitics["grow"].append(t_grow)
        self.time_statisitics["disj_mcs"].append(t_disj_mcs)

        self.call_statistics["#opt"].append(n_opt)
        self.call_statistics["#sat"].append(n_sat)
        self.call_statistics["#grow"].append(n_grow)
        self.call_statistics["#disj_mcs"].append(n_disj_mcs)
        self.call_statistics["#hs"].append(n_hs)
        self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
        self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)
        return best_expl

from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.utils.utils import get_expl
import time
from pysat.formula import CNF
from pyexplain.solvers.params import DisjointMCSes, Grow, OUSParallelIncrNaiveParams
from pyexplain.solvers.hittingSet import OptHS
import heapq as hq

class ParallelGreedyIncrNaiveExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: OUSParallelIncrNaiveParams, verbose=True, matching_table=None):
        assert isinstance(params, OUSParallelIncrNaiveParams), f"Expected {OUSParallelIncrNaiveParams} got {type(params)}"

        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

        # initialise data structures for tracking of information
        # BOUNDING OF EXPLANATION COST

        # OPTIMISATION MODEL
        self.opt_solvers = dict()

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
            "#hs": [], # number of sets to hit computed
            "#disj_mcs": [], # number of sets to hit computed
            "#hs_disj_mcs": [], # number of sets to hit computed with disj. mcs. enumeration
        })


    def preprocess(self, U: set, f, I0: set, Iend: set, end_time_timeout=None):
        CSPExplain.preprocess(self, U, f, I0, Iend)
        t_mip = 0

        for l in Iend - I0:
            # Formula to explain
            A = I0 | set({-l})

            # Fomula with reuse of satisfiable subsets
            F = Iend - set({l}) | set({-l})

            mcses = [set({-l})]

            # OPITMISATION MODEL
            tmip = time.time()
            self.opt_solvers[l] = OptHS(f, F, I0)
            self.opt_solvers[l].updateObjective(f, A)
            self.opt_solvers[l].addCorrectionSets(mcses)
            t_mip += (time.time() - tmip)

        self.time_statisitics["opt"].append(t_mip)

    def bestStep(self, f, Iend, I, increments=1, end_time_timeout=None):
        # BENCHMARK DATA
        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs = 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0

        expl_found = False

         # update interpretation
        self.I = set(I)

        # best cost
        remaining = list(Iend - I)

        # remove bounds on elements that are not in the remaining literals
        # to explain
        lb = []

        for lit in I.intersection(self.opt_solvers):
            self.opt_solvers[lit].delete()
            del self.opt_solvers[lit]

        # keep Track of best explanation
        best_expl, best_lit = None, None

        for lit in remaining:
            # things to explain
            A = I | set({-lit})

            # Fomula with reuse of satisfiable subsets
            F = Iend - set({lit}) | set({-lit})

            # updating the objective weights
            tmip = time.time()
            self.opt_solvers[lit].updateObjective(f, A)
            HS = self.opt_solvers[lit].OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt += 1

            # adding it to the heaaaap
            hq.heappush(lb, (sum(f(l) for l in HS), lit, HS))

        # initialising the best cost
        while(not expl_found):
            (_, lit, HS) = hq.heappop(lb)
            if self.verbose > 2:
                print(f"[{lit}] - HS \t= ", get_expl(self.matching_table, HS), f"[{sum(f(l) for l in HS)}]")

            # checking satisfiability only on the one with lowest cost
            tsat = time.time()
            sat, HS_model = self.checkSat(HS, phases=self.Iend)
            t_sat += (time.time() - tsat)
            n_sat +=1

            if not sat:
                expl_found = True
                best_lit = lit
                best_expl = HS
                break

            A = I | set({-lit})

            F = Iend - set({lit}) | set({-lit})

            tgrow = time.time()
            to_hit = self.grow(F=F, f=f, A=A, HS=HS, HS_model=HS_model, end_time_timeout=end_time_timeout)
            t_grow += (time.time() - tgrow)
            n_grow +=1
            n_hs +=len(to_hit)
            
            tmip = time.time()
            self.opt_solvers[lit].addCorrectionSets(to_hit)
            t_mip += (time.time() - tmip)
        
            # OPT Hitting SET
            tmip = time.time()
            HS = self.opt_solvers[lit].OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt += 1

            hq.heappush(lb, (sum(f(l) for l in HS), lit, HS))


        # delete optimisation model
        self.opt_solvers[best_lit].delete()
        del self.opt_solvers[best_lit]

        self.time_statisitics["opt"].append(t_mip)
        self.time_statisitics["sat"].append(t_sat)
        self.time_statisitics["grow"].append(t_grow)
        self.time_statisitics["disj_mcs"].append(t_disj_mcs)
        self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)

        self.call_statistics["#opt"].append(n_opt)
        self.call_statistics["#sat"].append(n_sat)
        self.call_statistics["#grow"].append(n_grow)
        self.call_statistics["#disj_mcs"].append(n_disj_mcs)
        self.call_statistics["#hs"].append(n_hs)
        self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)

        return best_expl

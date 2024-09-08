from pyexplain.utils.utils import get_expl
import time
from pysat.formula import CNF
from pyexplain.solvers.params import DisjointMCSes, Grow, OusIncrSharedParams
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import OptHS
from pyexplain.explain.csp_explain import CSPExplain


class GreedyIncrSharedExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: OusIncrSharedParams, verbose=True, matching_table=None):
        assert isinstance(params, OusIncrSharedParams), f"Expected {OusIncrSharedParams} got {type(params)}"
        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

        # initialise data structures for tracking of information
        self.lb = dict()
        self.ub = dict()

        self.opt_solvers = dict()

        self.time_statisitics.update({
            "opt": [],
            "sat": [],
            # grow with disj.mcs or maxsat
            "grow": [],
            "disj_mcs": [],
            # bootstrapping with disjoint mcs enumeration
            "postprocessing": [],
            "remaining": []
        })

        self.call_statistics.update({
            "#opt": [], # number of calls to otpimsiation solver
            "#sat": [], # number of calls to sat solver
            "#grow": [], # number of calls to grow
            "#hs": [], # number of sets to hit computed
            "#disj_mcs": [], 
            "#hs_disj_mcs": [], # number of sets to hit computed with disj. mcs. enumeration
            "#skipped": [], # literals explained skipped
            "#sat_subsets": []
        })

    def preprocess(self, U:set, f, I0: set, Iend: set, end_time_timeout=None):
        CSPExplain.preprocess(self, U, f, I0, Iend)
        t_mip = 0
        n_opt = 0

        # initialize costs
        Xbest = I0 | {-l for l in  Iend - I0}
        f_xbest = sum(f(l) for l in Xbest)

        # pre-compute the best cost
        for lit in Iend - I0:
            # initialising the Bounding
            A = I0 | set({-lit})

            # Fomula with reuse of satisfiable subsets
            F = Iend - set({lit}) | set({-lit})

            # BOUNDS initialisation
            self.lb[lit] = 0
            self.ub[lit] = f_xbest

            mcses = [set([-lit])]

            tmip = time.time()
            self.opt_solvers[lit] = OptHS(f, F, I0)
            self.opt_solvers[lit].updateObjective(f, A)
            self.opt_solvers[lit].addCorrectionSets(mcses)
            self.lb[lit] = sum(f(l) for l in self.opt_solvers[lit].OptHittingSet(end_time_timeout))
            t_mip += (time.time() - tmip)
            n_opt += 1

            self.time_statisitics["opt"].append(t_mip)
            self.call_statistics["#opt"].append(n_opt)

    def bestStep(self, f, Iend: set, I: set, end_time_timeout=None):
        t_best_step_start = time.time()
        t_mip, t_disj_mcs, t_post_processing,t_ous = 0, 0, 0, 0
        n_hs, n_hs_disj_mcs, n_opt, n_disj_mcs = 0, 0, 0, 0

        best_expl, best_lit = None, None

        # making sure that opt models are removed
        for lit in I.intersection(self.lb):
            del self.lb[lit]
            del self.ub[lit]

            # delete optimisation model
            self.opt_solvers[lit].delete()
            del self.opt_solvers[lit]

         # update interpretation
        self.I = set(I)

        # best cost
        remaining = list(Iend - I)

        # initialising the best cost
        for lit in remaining:
            # things to explain
            A = I | set({-lit})
            # Fomula with reuse of satisfiable subsets
            F = Iend - set({lit}) | set({-lit})

            # updating with new interpretation
            tmip = time.time()
            self.opt_solvers[lit].updateObjective(f, A)
            self.lb[lit] = sum(f(l) for l in self.opt_solvers[lit].OptHittingSet(end_time_timeout))
            t_mip += (time.time() - tmip)
            n_opt += 1

        if self.params.sort_literals:
            remaining.sort(key=lambda l: self.lb[l])

        skipped = 0

        # initialising the best cost
        best_cost = min(self.ub.values())

        # all satisfiable subsets found!
        all_sat_subsets = []
        
        for id, lit in enumerate(remaining):
            # active optimisation model
            self.hittingset_solver = self.opt_solvers[lit]

            A = I | set({-lit})
            F = Iend - set({lit}) | set({-lit})

            # expl is None when cutoff (timeout or cost exceeds current best Cost)
            tous = time.time()
            expl, cost_expl, sat_subsets = self.ous_incr_naive(f, F=F, A=A, end_time_timeout=end_time_timeout)
            t_ous += time.time() - tous

            # keep the sat_subsets
            all_sat_subsets += [(lit, sat_subset) for sat_subset in sat_subsets]
            self.lb[lit] = cost_expl

            if expl is None:
                skipped += 1
                continue

            # Always guaranteed, but safety check
            self.ub[lit] = cost_expl

            # store explanation
            if cost_expl <= best_cost:
                best_expl = expl
                best_lit = lit
                best_cost = cost_expl


        # post-process satisfiable subsets
        # optimal propagate it ?

        tpost = time.time()
        for lit in remaining:
            if lit == best_lit:
                continue

            F = Iend - set({lit}) | set({-lit})
            for li, sat_subset in all_sat_subsets:
                # don't add SS twice
                if li == lit:
                    continue
                C = F - sat_subset
                self.opt_solvers[lit].addCorrectionSet(C)
        t_post_processing += (time.time() - tpost)

        # literal already found, remove its cost
        del self.lb[best_lit]
        del self.ub[best_lit]

        # delete optimisation model
        self.opt_solvers[best_lit].delete()
        del self.opt_solvers[best_lit]

        # statistics
        self.call_statistics["#skipped"].append(skipped)

        self.time_statisitics["opt"].append(t_mip)
        self.time_statisitics["disj_mcs"].append(t_disj_mcs)
        self.time_statisitics["postprocessing"].append(t_post_processing)
        self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_disj_mcs - t_ous)
        self.call_statistics["#opt"].append(n_opt)
        self.call_statistics["#hs"].append(n_hs)
        self.call_statistics["#disj_mcs"].append(n_disj_mcs)
        self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
        self.call_statistics["#sat_subsets"].append(len(all_sat_subsets))

        return best_expl

    def ous_incr_naive(self, f, F, A, end_time_timeout=None):
        assert self.hittingset_solver is not None, "Making sure model ok!"
        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs = 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0

        #keeping track of satisfibale subsets
        sat_subsets = list()

        # initial best cost
        bestCost = min(self.ub.values())

        while(True):
            # Optimal Hitting set
            tmip = time.time()
            HS = self.hittingset_solver.OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt +=1


            tsat = time.time()

            # CHECKING SATISFIABILITY
            sat, HS_model = self.checkSat(HS, phases=self.Iend)
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

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)
                return HS, costHS, sat_subsets

            if costHS > bestCost:
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
                return None, costHS, sat_subsets

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
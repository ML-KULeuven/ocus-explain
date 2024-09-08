from pyexplain.utils.utils import get_expl
import time
from pysat.formula import CNF
from pyexplain.solvers.params import DisjointMCSes, Grow, OusIncrNaiveParams
from pyexplain.solvers.bestStep import BestStepComputer
from pyexplain.solvers.hittingSet import OptHS
from pyexplain.explain.csp_explain import CSPExplain



class GreedyIncrNaiveExplain(CSPExplain, BestStepComputer):
    def __init__(self, C: CNF, params: OusIncrNaiveParams, verbose=True, matching_table=None):
        assert isinstance(params, OusIncrNaiveParams), f"Expected {OusIncrNaiveParams} got {type(params)}"
        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        BestStepComputer.__init__(self, cnf=C, sat=self.sat,params=params)

        # initialise data structures for tracking of information
        # BOUNDING OF EXPLANATION COST
        self.lb = dict()
        self.ub = dict()

        # OPTIMISATION MODEL
        self.opt_solvers = dict()

        self.time_statisitics.update({
            "opt": [],
            "sat": [],
            # grow with disj.mcs or maxsat
            "grow": [],
            "disj_mcs": [],
            "remaining": []
        })

        self.call_statistics.update({
            "#opt": [], # number of calls to otpimsiation solver
            "#sat": [], # number of calls to sat solver
            "#grow": [], # number of calls to grow
            "#hs": [], # number of sets to hit computed
            "#disj_mcs": [], # number of sets to hit computed
            "#hs_disj_mcs": [], # number of sets to hit computed with disj. mcs. enumeration
            "#skipped": [] # literals explained skipped
        })

    def preprocess(self, U: set, f, I0: set, Iend: set, end_time_timeout=None):
        t_best_step_start = time.time()
        t_mip, t_disj_mcs = 0, 0
        n_opt, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0

        CSPExplain.preprocess(self, U, f, I0, Iend)

        # initialize costs
        Xbest = I0 | {-l for l in  Iend - I0}
        f_xbest = sum(f(l) for l in Xbest)

        for lit in Iend - I0:
            # Formula to explain
            A = I0 | set({-lit})

            # Fomula with reuse of satisfiable subsets
            F = Iend - set({lit}) | set({-lit})

            # BOUNDS initialisation
            self.lb[lit] = 0
            self.ub[lit] = f_xbest

            mcses = [set([-lit])]

            tmip = time.time()
            # OPITMISATION MODEL
            self.opt_solvers[lit] = OptHS(f, F, I0)
            self.opt_solvers[lit].updateObjective(f, A)
            self.opt_solvers[lit].addCorrectionSets(mcses)
            self.lb[lit] = sum(f(l) for l in self.opt_solvers[lit].OptHittingSet(end_time_timeout))
            t_mip += (time.time() - tmip)
            n_opt += 1

        self.time_statisitics["opt"].append(t_mip)
        self.time_statisitics["disj_mcs"].append(t_disj_mcs)
        self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_disj_mcs)

        self.call_statistics["#opt"].append(n_opt)
        self.call_statistics["#hs"].append(n_hs)
        self.call_statistics["#disj_mcs"].append(n_disj_mcs)
        self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)

    def bestStep(self, f, Iend, I, end_time_timeout=None):
        t_best_step_start = time.time()
        t_mip, t_disj_mcs,t_ous = 0, 0, 0
        n_opt, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0

        # Benchmark data
        skipped = 0

        # keep Track of best explanation
        best_expl, best_lit = None, None

         # update interpretation
        self.I = set(I)

        # best cost
        remaining = list(Iend - I)

        for lit in I.intersection(self.lb):
            del self.lb[lit]
            del self.ub[lit]

            # delete optimisation model
            self.opt_solvers[lit].delete()
            del self.opt_solvers[lit]

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

        best_cost = min(self.ub.values())
        for lit in remaining:
            # things to explain
            A = I | set({-lit})
            F = Iend - set({lit}) | set({-lit})

            # active optimisation model
            self.hittingset_solver = self.opt_solvers[lit]

            # expl is None when cutoff (timeout or cost exceeds current best Cost)
            tous = time.time()
            expl, cost_expl = self.ous_incr(f, F=F, A=A, l=lit, end_time_timeout=end_time_timeout)
            t_ous += time.time() - tous

            self.lb[lit] = cost_expl

            if expl is None:
                skipped += 1
                continue

            self.ub[lit] = cost_expl

            # store explanation
            if cost_expl <= best_cost:
                best_expl = expl
                best_lit = lit
                best_cost = cost_expl

        # literal already found, remove its cost
        del self.lb[best_lit]
        del self.ub[best_lit]

        # delete optimisation model
        self.opt_solvers[best_lit].delete()
        del self.opt_solvers[best_lit]

        # statistics
        self.call_statistics["#skipped"].append(skipped)

        # call statistics
        self.time_statisitics["opt"].append(t_mip)
        self.time_statisitics["disj_mcs"].append(t_disj_mcs)
        self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_disj_mcs-t_ous)

        self.call_statistics["#opt"].append(n_opt)
        self.call_statistics["#hs"].append(n_hs)
        self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
        self.call_statistics["#disj_mcs"].append(n_disj_mcs)

        return best_expl

    def ous_incr(self, f, F, A, l, nsteps=None, end_time_timeout=None):
        assert self.hittingset_solver is not None, "Making sure model ok!"

        # STATISTICAL DATA
        t_best_step_start = time.time()
        t_sat, t_mip, t_grow, t_disj_mcs = 0, 0, 0, 0
        n_sat, n_opt, n_grow, n_hs, n_hs_disj_mcs, n_disj_mcs = 0, 0, 0, 0, 0, 0
        step_count  = 0

        # initial best cost
        best_cost = min(self.ub.values())

        # COST of current Hitting Set
        costHS = 0

        while(True):
            # MAXIMUM NUMBER OF STEPS
            if nsteps is not None and step_count == nsteps:
                # call statistics
                self.time_statisitics["opt"].append(t_mip)
                self.time_statisitics["sat"].append(t_sat)
                self.time_statisitics["grow"].append(t_grow)
                self.time_statisitics["disj_mcs"].append(t_disj_mcs)
                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
                return None, costHS

            # Hitting Set computation
            tmip = time.time()
            HS = self.hittingset_solver.OptHittingSet(end_time_timeout)
            t_mip += (time.time() - tmip)
            n_opt += 1

            if self.verbose > 1:
                print("\nHS\t= ", get_expl(self.matching_table, HS), f"({HS})")

            # SATISFIABILITY CHECK
            tsat = time.time()
            sat, HS_model = self.checkSat(HS, phases=self.Iend)
            t_sat += (time.time() -tsat)
            n_sat += 1

            costHS = sum(f(l) for l in HS)

            # OUS FOUND?
            if not sat:
                # call statistics
                # call statistics
                self.time_statisitics["opt"].append(t_mip)
                self.time_statisitics["sat"].append(t_sat)
                self.time_statisitics["grow"].append(t_grow)
                self.time_statisitics["disj_mcs"].append(t_disj_mcs)
                self.time_statisitics["remaining"].append(time.time() - t_best_step_start-t_mip-t_sat-t_grow-t_disj_mcs)

                self.call_statistics["#opt"].append(n_opt)
                self.call_statistics["#sat"].append(n_sat)
                self.call_statistics["#grow"].append(n_grow)
                self.call_statistics["#hs"].append(n_hs)
                self.call_statistics["#disj_mcs"].append(n_disj_mcs)
                self.call_statistics["#hs_disj_mcs"].append(n_hs_disj_mcs)
                return HS, costHS

            if costHS > best_cost:
                # Cost check is added here 
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
                return None, costHS

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

            step_count += 1


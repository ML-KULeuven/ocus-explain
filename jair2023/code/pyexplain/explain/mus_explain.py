import time
from pyexplain.solvers.bestStep import optimalPropagate
from pysat.formula import WCNF, CNF
from pysat.examples.musx import MUSX
from pyexplain.explain.csp_explain import CSPExplain
from pyexplain.solvers.params import MUSParams


class MUSExplain(CSPExplain):
    def __init__(self, C: CNF, params: MUSParams, verbose=False, matching_table=None):
        assert isinstance(params, MUSParams), f"Expected {MUSParams} got {type(params)}"
        super().__init__(C=C,verbose=verbose, matching_table=matching_table)
        self.params = params

        self.time_statisitics.update({
            "tavg_greedy_explain": [],
        })


    def explain(self, U: set, f, I0: set, prev_expl_seq=None, params=None, end_time_timeout=None, fname=None):
        tstart_explain = time.time() - self.offset_time_zero
        # check literals of I are all user vocabulary
        assert all(True if abs(lit) in U else False for lit in I0), f"Part of supplied literals not in U (user variables): {lit for lit in I if lit not in U}"

        # Initialise the sat solver with the cnf
        assert self.sat.solve_limited(assumptions=I0, expect_interrupt=True), f"CNF is unsatisfiable with given assumptions {I0}."

        # Explanation sequence
        self.E = []

        I = set(I0)

        # Most precise intersection of all models of C project on U
        Iend = optimalPropagate(U=U, I=I, sat=self.sat)

        tstart = time.time()
        super().preprocess(U, f, I, Iend, end_time_timeout)
        self.time_statisitics["preprocess"] = time.time() - tstart

        prev_expl_step = 0

        # print("#Literals to explain=", len(Iend))
        # print(f"#Lits not relevant in U [{len(set(abs(l) for l in U))}]: ", len(set(abs(l) for l in U) & set(abs(l) for l in Iend)))
        # print("#Literals explained=", len(I))

        while(len(Iend - I) > 0):
            costExpl = 0
            # Compute optimal explanation explanation assignment to subset of U.
            tstart = time.time()
            costExpl, Ei = self.bestStep(f, U, I, end_time_timeout)

            # facts used
            Ibest = I & Ei

            # New information derived "focused" on
            Nbest = optimalPropagate(U=U, I=Ibest, sat=self.sat) - I
            print(len(Nbest))

            assert len(Nbest - Iend) == 0

            self.E.append({
                "constraints": list(Ibest),
                "derived": list(Nbest),
                "cost": costExpl
            })

            if prev_expl_seq:
                Nbest = set(prev_expl_seq[prev_expl_step]["derived"])
                prev_expl_step += 1

            I |= Nbest

            self.call_statistics["explained"] += len(Nbest)

            if self.verbose > 0:
                self.print_expl(Ibest)
                print(f"\nOptimal explanation \t {len(Iend-I)}/{len(Iend-I0)} \t {Ibest} => {Nbest}\n")
                self.print_statistics()

            if fname and params:
                self.export_statistics(params=params, fname=fname)

            self.time_statisitics["explain"].append(time.time() - tstart)
            self.time_statisitics["cumul_explain"].append(time.time() - tstart_explain)

        self.time_statisitics["totalTime"] = time.time() - tstart_explain
        return self.E

    def MUSExtraction(self, C, end_time_timeout=None):
        wcnf = WCNF()
        wcnf.extend(self.cnf.clauses)
        wcnf.extend([[l] for l in C], [1]*len(C))
        with MUSX(wcnf, verbosity=0) as musx:
            mus = musx.compute()
            # gives back positions of the clauses !!
            return set(C[i-1] for i in mus)

    def candidate_explanations(self, U, I: set, end_time_timeout=None):
        candidates = []
        # kinda hacking here my way through I and C
        J = optimalPropagate(U=U, I=I, sat=self.sat) - I

        mus_times = []
        for a in J - I:
            unsat = list(set({-a}) | I)
            tstart = time.time()
            X = self.MUSExtraction(unsat)
            mus_times.append(time.time() - tstart)
            candidates.append(X)

        t_avg_greedy_beststep = sum(mus_times)/len(mus_times)
        self.time_statisitics["tavg_greedy_explain"].append(t_avg_greedy_beststep)
        return candidates

    def bestStep(self, f, U, I, end_time_timeout=None):
        Candidates = []
        cands = self.candidate_explanations(U, I, end_time_timeout)
        for cand in cands:
            cost_cand = sum(f(l) for l in cand)
            Candidates.append((cost_cand, cand))

        return min(Candidates, key=lambda cand: cand[0])


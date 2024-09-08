from threading import Timer
from pyexplain.utils.utils import get_expl
import time
from pyexplain.solvers.bestStep import optimalPropagate
from ..solvers.params import BestStepParams, ExplanationComputer
from pysat.formula import CNF
from pysat.solvers import Solver

import json
from pathlib import Path

class CSPExplain(object):
    def __init__(self, C: CNF, verbose=False, matching_table=None):
        self.offset_time_zero = time.time()
        self.cnf = C

        self.verbose = verbose

        if self.verbose > 1:
            print("Expl:")
            print("\tcnf:", len(C.clauses), C.nv)
        if self.verbose > 2:
            print("\n\tcnf:", C.clauses)

        # Initialise the sat solver with the cnf
        self.sat = Solver(bootstrap_with=C.clauses)
        assert self.sat.solve_limited(expect_interrupt=True), f"CNF is unsatisfiable"

        # explanation sequence
        self.E = []

        # matching table
        self.matching_table = matching_table

        # initial interpretation
        self.I0 = None
        self.I = None
        self.Iend = None

        # keeping track of the statistics
        self.time_statisitics = {
            # General time statistics
            "totalTime": 0,
            "timeout": 0,
            "timedout": False,
            "explain": [],
            "cumul_explain": [],
            "preprocess":0
        }

        # keep track of the calls
        self.call_statistics = {
            "explained":0,
        }
        self.offset_time_zero = time.time() - self.offset_time_zero

    def bestStep(self, f, Iend: set, I: set, end_time_timeout=None):
        raise NotImplementedError("Please implemnt this method")

    def preprocess(self, U: set, f, I0: set, Iend: set, end_time_timeout=None):
        self.I0 = set(I0)
        self.I = set(I0)
        self.Iend = set(Iend)
        self.U = set(U) | set(-l for l in U)

        # checking everything is correct
        if self.verbose > 1:
            print('Preprocess')
            print("\tU:", len(U))
            print("\tf:", f)
            print("\tI0:", len(I0))
            print("\tIend:", len(Iend))


    def explain_1_lit(self, lit, f, I0: set, end_time_timeout=None):
        assert type(lit) is int, f"Type of given lit is {type(lit)} expected int."
        assert type(I0) is set,  f"Type of given initial intepretation is {type(I0)} expected set."

        U = set(abs(l) for l in I0) | set({abs(lit)})
        I = I0

        Iend = optimalPropagate(U=U, I=I0, sat=self.sat)

        # keep track of explanation config-specific information
        tstart = time.time()
        self.preprocess(U, f, I0, Iend)
        self.time_statisitics["preprocess"] = time.time() - tstart

        expl = self.bestStep(f, Iend, I)

        # difficulty of explanation
        costExpl = sum(f(l) for l in expl)

        # facts & constraints used
        Ibest = I & expl

        # New information derived "focused" on
        Nbest = optimalPropagate(U=U, I=Ibest, sat=self.sat) - I0


        return {
            "constraints": list(Ibest),
            "derived": list(Nbest),
            "cost": costExpl
        }

    def explain_1_step(self, U: set, f, I0: set, end_time_timeout=None):
        assert type(U) is set, f"Type of given User variables is {type(U)} expected set."
        assert type(I0) is set,  f"Type of given initial intepretation is {type(I0)} expected set."

        # check literals of I are all user vocabulary
        assert all(True if abs(lit) in U else False for lit in I0), f"Part of supplied literals not in U (user variables): {lit for lit in I if lit not in U}"

        # Initialise the sat solver with the cnf
        assert self.sat.solve_limited(assumptions=I0,expect_interrupt=True), f"CNF is unsatisfiable with given assumptions {I0}."

        # Most precise intersection of all models of C project on U
        Iend = optimalPropagate(U=U, I=I0, sat=self.sat)

        # keep track of explanation config-specific information
        tstart = time.time()
        self.preprocess(U, f, I0, Iend)
        self.time_statisitics["preprocess"] = time.time() - tstart

        tstart = time.time()
        expl = self.bestStep(f, Iend, I0)
        self.time_statisitics["explain"].append(time.time() - tstart)

        # difficulty of explanation
        costExpl = sum(f(l) for l in expl)

        # facts & constraints used
        Ibest = I0 & expl

        # New information derived "focused" on
        Nbest = optimalPropagate(U=U, I=Ibest, sat=self.sat) - I0

        return {
            "constraints": list(Ibest),
            "derived": list(Nbest),
            "cost": costExpl
        }

    def explain(self, U: set, f, I0: set, end_time_timeout=None, params=None, fname=None):

        if end_time_timeout:
            def interrupt(s):
                s.interrupt()

            timer = Timer(end_time_timeout - time.time(), interrupt, [self.sat])
            timer.start()

        tstart_explain = time.time() - self.offset_time_zero

        # check literals of I are all user vocabulary
        assert all(True if abs(lit) in U else False for lit in I0), f"Part of supplied literals not in U (user variables): {lit for lit in I if lit not in U}"

        # Initialise the sat solver with the cnf
        assert self.sat.solve_limited(assumptions=I0,expect_interrupt=True), f"CNF is unsatisfiable with given assumptions {I0}."

        # Explanation sequence
        self.E = []

        I0 = set(I0)

        # Most precise intersection of all models of C project on U

        Iend = optimalPropagate(U=U, I=I0, sat=self.sat)

        if self.verbose > 1:
            print("\nIend\t= ", get_expl(self.matching_table, Iend), f"({Iend})")

        # keep track of information
        tstart_preprocessing = time.time()
        self.preprocess(U, f, I0, Iend, end_time_timeout)
        self.time_statisitics["preprocess"] = time.time() - tstart_preprocessing

        I = set(I0) # copy

        while(len(Iend - I) > 0):
            # finding the next best epxlanation
            tstart = time.time()
            expl = self.bestStep(f, Iend, I, end_time_timeout)

            # difficulty of explanation
            costExpl = sum(f(l) for l in expl)

            # facts & constraints used
            Ibest = I & expl

            # New information derived "focused" on
            Nbest = optimalPropagate(U=U, I=Ibest, sat=self.sat) - I

            assert len(Nbest - Iend) == 0

            self.E.append({
                "constraints": list(Ibest),
                "derived": list(Nbest),
                "cost": costExpl
            })

            I |= Nbest
            self.call_statistics["explained"] += len(Nbest)

            if self.verbose > 0:
                # self.print_expl(Ibest)
                print(f"\nOptimal explanation \t {len(Iend-I)}/{len(Iend-I0)} \tElapsed time=", round(time.time() - tstart_explain), "s\n")
                print("\t", get_expl(self.matching_table, Ibest, Nbest))
                # self.print_statistics()

            self.time_statisitics["explain"].append(time.time() - tstart)
            self.time_statisitics["cumul_explain"].append(time.time() - tstart_explain)

            if fname and params:
                self.export_statistics(params=params, fname=fname)

        self.time_statisitics["totalTime"] = time.time() - tstart_explain
        return list(self.E)

    def print_statistics(self):
        print("texpl=", round(self.time_statisitics["explain"][-1], 2), "s\n")

    def export_statistics(self, params: BestStepParams=None, fname=""):
        if fname == "":
            return

        json_statistics = {
            "time": self.time_statisitics,
            "numbers": self.call_statistics,
            "explanation": self.E,
            'params': params.to_dict() if params is not None else dict()
        }

        if not Path(fname).parent.exists():
            Path(fname).parent.mkdir(parents=True)

        file_path = Path(fname)

        with file_path.open('w') as f:
            json.dump(json_statistics, f)
        
        print("Dumped:\n\t", fname)

    def __del__(self):
        if hasattr(self, 'sat') and self.sat:
            self.sat.delete()

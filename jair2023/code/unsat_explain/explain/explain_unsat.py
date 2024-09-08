import itertools
from pyexplain.solvers.bestStep import optimalPropagate
from unsat_explain.solvers.propagator import propagate_interpretation, unsat_optimal_propagate
from pysat.formula import CNF
from pysat.solvers import Solver


class CSPUnsatExplain(object):
    def __init__(self, C: CNF, verbose=False, matching_table=None):
        self.cnf = C
        self.verbose = verbose

        if self.verbose > 1:
            print("Expl:")
            print("\tcnf:", len(C.clauses), C.nv)
        if self.verbose > 2:
            print("\n\tcnf:", C.clauses)

        # Initialise the sat solver with the cnf
        self.sat = Solver(bootstrap_with=C.clauses)

        # matching table
        self.matching_table = matching_table

        # initial interpretation
        self.I0 = None
        self.I = None
        self.Iend = None

    def bestStep(self, f, Iend: set, I: set):
        raise NotImplementedError("Please implemnt this method")

    def preprocess(self, U: set, f, I0: set, Iend: set):
        self.I0 = set(I0)
        self.I = set(I0)
        self.Iend = set(Iend)
        self.U = set(U) | set(-l for l in U)

        # checking everything is correct
        if self.verbose > 1:
            print('Preprocess')
            print("\tU:", len(U))
            print("\tf:", f)
            print(f"\t{I0=}")
            print(f"\t{Iend=}")

    def unsat_explain_1_step(self, f, U, assumptions, I0):
        assert type(I0) is set,  f"Type of given initial intepretation is {type(I0)} expected set."

        U = set(U) | set(-l for l in U)
        I = set(I0)

        Iend = propagate_interpretation(U=U, I=assumptions + list(I0), sat=self.sat)

        # keep track of explanation config-specific information
        self.preprocess(U, f, I0 | set(assumptions), Iend)

        expl = self.bestStep(f, Iend, I | set(assumptions))

        # difficulty of explanation
        costExpl = sum(f(l) for l in expl)

        # facts & constraints used
        Ibest = I & expl

        # New information derived "focused" on
        Nbest = unsat_optimal_propagate(U=U, I=Ibest, sat=self.sat) - I0

        return {
            "constraints": list(Ibest),
            "derived": list(Nbest),
            "cost": costExpl
        }

    def unsat_explain(self, f, U, assumptions, I0):
        assert type(I0) is set,  f"Type of given initial intepretation is {type(I0)} expected set."
        """
            Generate step-wise explanations of UNSAT 
            for Boolean variables 
        """
        ## Interpretation until inconsistency

        U = set(U) | set(-l for l in U)
        I = set(I0) # | set(assumptions)

        Iend = propagate_interpretation(U=U, I=assumptions + list(I), sat=self.sat)

        # keep track of explanation config-specific information
        self.preprocess(U, f, I | set(assumptions), Iend)

        ## Sequence
        expl_seq = []
        steps = 0

        sat, _ = self.checkSat(I)

        while(sat):
            expl = self.bestStep(f, Iend, I | set(assumptions))

            # difficulty of explanation
            costExpl = sum(f(l) for l in expl)

            # facts & constraints used
            Ibest = I & expl
            Sbest = set(assumptions) & expl

            # New information derived "focused" on
            Nbest = unsat_optimal_propagate(U=U, I=Ibest | Sbest, sat=self.sat)

            if Nbest is None:
                print("Contradiction found!")
                expl_seq.append({
                    "facts": list(Ibest),
                    "constraints": list(Sbest),
                    "derived": set(),
                    "cost": costExpl
                })
                break

            Nbest -= I
            Nbest -= set(assumptions)

            I |= Nbest

            expl_seq.append({
                "facts": list(Ibest),
                "constraints": list(Sbest),
                "derived": list(Nbest),
                "cost": costExpl
            })

            ## TODO: Check the sat here!
            sat, _ = self.checkSat(I)

            steps +=1

        return expl_seq
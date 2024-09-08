
import time
from ..utils.utils import get_expl
from .params import BestStepParams, Grow, Interpretation, Weighing
from ..utils.exceptions import UnsatError

# pysat imports
from pysat.formula import CNF, WCNF
from pysat.solvers import Solver
from pysat.examples.rc2 import RC2


def optimalPropagate(sat, I=set(), U=None, end_time_timeout=None):
    """
    optPropage produces the intersection of all models of cnf more precise
    projected on focus.

    Improvements:
    - Extension 1:
        + Reuse solver only for optpropagate
    - Extension 2:
        + Reuse solver for all sat calls
    - Extension 3:
        + Set phases

    Args:
    cnf (list): CNF C over V:
            hard puzzle problems with assumptions variables to activate or
            de-active clues.
    I (list): partial interpretation

    U (list):
        +/- literals of all user variables
    """
    solved = sat.solve_limited(assumptions=list(I), expect_interrupt=True)

    if not solved:
        raise UnsatError(I)

    model = set(sat.get_model())
    if U:
        model = set(l for l in model if (abs(l) in U or -abs(l) in U))

    bi = sat.nof_vars() + 1

    while(True):
        sat.add_clause([-bi] + [-lit for lit in model])
        solved = sat.solve_limited(assumptions=list(I) + [bi], expect_interrupt=True)

        if not solved:
            sat.add_clause([-bi])
            return model

        new_model = set(sat.get_model())
        model = model.intersection(new_model)


class BestStepComputer(object):
    def __init__(self, cnf: CNF, sat: Solver, params: BestStepParams):
        self.sat_solver = sat
        self.cnf = cnf
        self.opt_model = None
        self.I0 = None
        self.I = None
        self.Iend = None

        # check parameters
        params.checkParams()
        self.params = params

    def disjoint_mcses_subsets(self, f, F, A, HS=None, subsets=None, end_time_timeout=None):
        # adding a at most k constriant on literals to expalin
        wcnf = WCNF()

        # HARD clauses
        wcnf.extend(self.cnf.clauses)

        if HS is not None:
            wcnf.extend([[l] for l in HS])

        if subsets is not None:
            neg_subsets = []
            for subset in subsets:
                neg_subsets.append([-l for l in set(subset)&F])
            wcnf.extend(neg_subsets)

        # SOFT clauses to grow
        if self.params.disjoint_mcs_interpretation is Interpretation.INITIAL:
            remaining = list(self.I0 - HS)
        elif self.params.disjoint_mcs_interpretation is Interpretation.ACTUAL:
            remaining = list(self.I - HS)
        elif self.params.disjoint_mcs_interpretation is Interpretation.FINAL:
            remaining = list(self.Iend - HS)
        elif self.params.disjoint_mcs_interpretation is Interpretation.FULL:
            remaining = list(A - HS)

        remaining_clauses = [[l] for l in remaining]

        # weighing scheme to apply
        if self.params.disjoint_mcs_weighing is Weighing.POSITIVE:
            weights = [f(l) for l in remaining]
        elif self.params.disjoint_mcs_weighing is Weighing.INVERSE:
            max_weight = max(f(l) for l in remaining) + 1
            weights = [max_weight - f(l) for l in remaining]
        elif self.params.disjoint_mcs_weighing is Weighing.UNIFORM:
            weights = [1] * len(remaining)

        # cost is associated for assigning a truth value to literal not in
        # contrary to A.
        wcnf.extend(clauses=remaining_clauses, weights=weights)

        # (unit-size MCSes are stored separately)
        to_hit, S, new_subsets = [], set(HS), []

        with RC2(wcnf, adapt=True, exhaust=True, incr=True, minz=True) as oracle:
            if self.params.maxsat_polarity and hasattr(oracle, 'oracle'):
                oracle.oracle.set_phases(literals=list(self.Iend))

            # iterating over MaxSAT solutions
            improved = True
            while improved:
                improved = False
                # a new MaxSAT model
                if end_time_timeout and (time.time() > end_time_timeout):
                    break

                SS = oracle.compute()
                if SS is None:
                    # no model => no more disjoint MCSes
                    break
                new_subsets.append(SS)

                if self.verbose > 2:
                    print("\nMCS-enum: SS\t= ", get_expl(self.matching_table, SS))

                # extracting the MCS corresponding to the model
                C = F - set(SS)

                if self.verbose > 2:
                    print("MCS-enum: MCS\t= ", get_expl(self.matching_table, C))
                    print("MCS-enum: MCS (C & A)\t= ", get_expl(self.matching_table, C & A), "\n")

                # unit size or not?
                to_hit.append(C)

                # blocking the MCS;
                # next time, all these clauses will be satisfied
                for l in C & A:
                    improved = True
                    oracle.add_clause([l])

                S |= (C & A)

            # RC2 will be destroyed next; let's keep the oracle time
            self.disj_time = oracle.oracle_time()

        return to_hit, S, new_subsets

    def disjoint_mcses(self, f, F, A, HS=set(), end_time_timeout=None):
        # adding a at most k constriant on literals to expalin
        wcnf = WCNF()

        # HARD clauses
        wcnf.extend(self.cnf.clauses)

        if len(HS) > 0:
            wcnf.extend([[l] for l in HS])

        # SOFT clauses to grow
        if self.params.disjoint_mcs_interpretation is Interpretation.INITIAL:
            remaining = list(self.I0 - HS)
        elif self.params.disjoint_mcs_interpretation is Interpretation.ACTUAL:
            remaining = list(self.I - HS)
        elif self.params.disjoint_mcs_interpretation is Interpretation.FINAL:
            remaining = list(self.Iend - HS)
        elif self.params.disjoint_mcs_interpretation is Interpretation.FULL:
            remaining = list(A - HS)

        remaining_clauses = [[l] for l in remaining]

        # weighing scheme to apply
        if self.params.disjoint_mcs_weighing is Weighing.POSITIVE:
            weights = [f(l) for l in remaining]
        elif self.params.disjoint_mcs_weighing is Weighing.INVERSE:
            max_weight = max(f(l) for l in remaining) + 1
            weights = [max_weight - f(l) for l in remaining]
        elif self.params.disjoint_mcs_weighing is Weighing.UNIFORM:
            weights = [1] * len(remaining)

        # cost is associated for assigning a truth value to literal not in
        # contrary to A.
        wcnf.extend(clauses=remaining_clauses, weights=weights)

        # (unit-size MCSes are stored separately)
        to_hit, S = [], set(HS)

        with RC2(wcnf, adapt=True, exhaust=True, incr=True, minz=True) as oracle:
            if self.params.maxsat_polarity and hasattr(oracle, 'oracle'):
                oracle.oracle.set_phases(literals=list(self.Iend))

            # iterating over MaxSAT solutions
            improved = True
            while improved:
                improved = False
                # a new MaxSAT model
                if end_time_timeout and (time.time() > end_time_timeout):
                    break
                SS = oracle.compute()

                if SS is None:
                    # no model => no more disjoint MCSes
                    break

                if self.verbose > 2:
                    print("\nMCS-enum: SS\t= ", get_expl(self.matching_table, SS))

                # extracting the MCS corresponding to the model
                C = F - set(SS)

                if self.verbose > 2:
                    print("MCS-enum: MCS\t= ", get_expl(self.matching_table, C))
                    print("MCS-enum: MCS (C & A)\t= ", get_expl(self.matching_table, C & A), "\n")

                # unit size or not?
                to_hit.append(C)

                # blocking the MCS;
                # next time, all these clauses will be satisfied
                for l in C & A:
                    improved = True
                    oracle.add_clause([l])

                S |= (C & A)

            # RC2 will be destroyed next; let's keep the oracle time
            self.disj_time = oracle.oracle_time()

        return to_hit

    def grow(self, f, F, A, HS, HS_model, end_time_timeout=None):
        # no actual grow needed if 'HS_model' contains all user vars
        if self.params.grow is Grow.DISABLED:
            return [F - HS]
        elif self.params.grow is Grow.SAT:
            return [F - HS_model]
        elif self.params.grow is Grow.SUBSETMAX:
            phases=None
            if self.params.interpretation is Interpretation.INITIAL:
                phases = set(self.I0)
            elif self.params.interpretation is Interpretation.ACTUAL:
                phases = set(self.I)
            elif self.params.interpretation is Interpretation.FINAL:
                phases = set(self.Iend)
            elif self.params.interpretation is Interpretation.FULL:
                phases = set(A)
            else:
                phases = set(self.Iend)
            sat, SS = self.subsetmax_sat(F=F, S=HS, phases=phases)
            return [F - SS]
        elif self.params.grow is Grow.MAXSAT:
            SS = self.grow_maxsat(f=f, A=A, HS=HS, end_time_timeout=end_time_timeout)
            return [F - SS]
        elif self.params.grow is Grow.CORR_GREEDY:
            mcs_clauses = self.correction_subsets_maxsat_then_greedy(
                    f=f, F=F, A=A, HS=HS, end_time_timeout=end_time_timeout)
            return mcs_clauses
        elif self.params.grow is Grow.DISJ_MCS:
            mcs_clauses = self.disjoint_mcses(f=f, F=F, A=A, HS=HS, end_time_timeout=end_time_timeout)
            return mcs_clauses
        elif self.params.grow is Grow.CORRECTION_SUBSETS_SAT:
            mcs_clauses = self.correction_subsets_sat(F=F, A=A, HS=HS)
            return mcs_clauses
        elif self.params.grow is Grow.CORRECTION_SUBSETMAX_SAT:
            mcs_clauses = self.correction_subsetmax_sat(F=F, A=A, HS=HS)
            return mcs_clauses
        else:
            raise NotImplementedError("Grow")

    def correction_subsets_maxsat_then_greedy(self, f, F, A, HS=None, end_time_timeout=None):
        correction_subsets = []

        if HS is None:
            HS = set()
        # Take a copy ex HSp = {x1, x2}
        # HSp = HS projected on the `useful` literals of the formula
        HSp = set(HS)
        ## start from a good solution! S = {x1, x2, ... -x5}
        SSp = self.grow_maxsat(f, A, HSp, end_time_timeout)

        improved = (HSp != SSp)
        while (improved):
            # Keeping track of the Correciton SUBsets
            C = F - SSp
            correction_subsets.append(C)

            # project the new correction subset on the useful literals of
            # the formula
            HS, HSp = HSp, (HSp | (A & C))

            # computing a new -- satisfiable! -- subset
            sat, SSp = self.checkSat(HSp, phases=self.Iend)

            improved = (HS != HSp) & sat

        return correction_subsets

    def grow_maxsat(self, f, A, HS, end_time_timeout=None):
        remaining, weights = None, None
        wcnf = WCNF()

        # HARD clauses
        wcnf.extend(self.cnf.clauses)

        wcnf.extend([[l] for l in HS])

        # SOFT clauses to grow
        if self.params.interpretation is Interpretation.INITIAL:
            remaining = list(self.I0 - HS)
        elif self.params.interpretation is Interpretation.ACTUAL:
            remaining = list(self.I - HS)
        elif self.params.interpretation is Interpretation.FINAL:
            remaining = list(self.Iend - HS)
        elif self.params.interpretation is Interpretation.FULL:
            remaining = list(A - HS)

        remaining_clauses = [[l] for l in remaining]

        if self.params.maxsat_weighing is Weighing.POSITIVE:
            weights = [f(l) for l in remaining]
        elif self.params.maxsat_weighing is Weighing.INVERSE:
            max_weight = max(f(l) for l in remaining) + 1
            weights = [max_weight - f(l) for l in remaining]
        elif self.params.maxsat_weighing is Weighing.UNIFORM:
            weights = [1] * len(remaining)

        # cost is associated for assigning a truth value to literal not in
        # contrary to A.
        wcnf.extend(clauses=remaining_clauses, weights=weights)

        # solve the MAXSAT problem
        with RC2(wcnf, adapt=True, exhaust=True, incr=True, minz=True) as s:
            if self.params.maxsat_polarity and hasattr(s, 'oracle'):
                s.oracle.set_phases(literals=list(self.Iend))

            if end_time_timeout and (time.time() > end_time_timeout):
                return HS

            t_model = s.compute()

            if t_model is None:
                return None

            return set(t_model)

    def correction_subsets_sat(self, F, A, HS):
        if self.params.interpretation is Interpretation.INITIAL:
            phases = set(self.I0)
        elif self.params.interpretation is Interpretation.ACTUAL:
            phases = set(self.I)
        elif self.params.interpretation is Interpretation.FINAL:
            phases = set(self.Iend)
        elif self.params.interpretation is Interpretation.FULL:
            phases = set(A)
        else:       
            phases = set(self.Iend)
        # used interpretation
        # Take a copy ex HSp = {x1, x2}
        # HSp = HS projected on the `useful` literals of the formula
        correction_subsets = []
        HSp = set(HS)
        ## start from a good solution! S = {x1, x2, ... -x5}
        sat, SSp = self.checkSat(HSp, phases=phases)

        if hasattr(self, "matching_table") and self.verbose > 2:
            print("\n----- start corr subsets ------\n")
            print("\nSS \t = ", get_expl(self.matching_table, SSp))
        elif self.verbose > 2:
            print("\n----- start corr subsets ------\n")
            print("\nSS \t = ", SSp)

        while (sat):
            if self.verbose > 2:
                print("\n sat \t = ", sat)
            # Keeping track of the Correciton SUBsets
            C = F - SSp
            correction_subsets.append(C)

            if hasattr(self, "matching_table") and self.verbose > 2:
                print("\nMCS \t = ", get_expl(self.matching_table, C))
            elif self.verbose > 2:
                print("\nMCS \t = ", C)

            # project the new correction subset on the useful literals of
            # the formula
            HS, HSp = HSp, (HSp | (A & C))

            # computing a new -- satisfiable! -- subset
            sat, SSp = self.checkSat(HSp, phases=phases)

            if hasattr(self, "matching_table") and self.verbose > 2:
                print("\nSS \t= ", get_expl(self.matching_table, HS), "->", get_expl(self.matching_table, HSp), "->", get_expl(self.matching_table, SSp))
            elif self.verbose > 2:
                print("\nSS \t = ", HS, "->", HSp , "->", SSp)

        if self.verbose > 2:
            print("\n----- end corr subsets ------\n")
        return correction_subsets

    def correction_subsetmax_sat(self, F, A, HS):
        if self.params.interpretation is Interpretation.INITIAL:
            I = set(self.I0)
        elif self.params.interpretation is Interpretation.ACTUAL:
            I = set(self.I)
        elif self.params.interpretation is Interpretation.FINAL:
            I = set(self.Iend)
        elif self.params.interpretation is Interpretation.FULL:
            I = set(A)
        else:
            I = set(self.Iend)
        # used interpretation
        # Take a copy ex HSp = {x1, x2}
        # HSp = HS projected on the `useful` literals of the formula
        correction_subsets = []

        HSp = set(HS)
        ## start from a good solution! S = {x1, x2, ... -x5}
        sat, SSp = self.subsetmax_sat(HSp, F, phases=I)
        assert sat, "Ensure it's sat before growing"

        if hasattr(self, "matching_table") and self.verbose > 2:
            print("\nSS \t = ", get_expl(self.matching_table, SSp))
        elif self.verbose > 2:
            print("\nSS \t = ", SSp)

        while (sat):
            # Keeping track of the Correciton SUBsets
            C = F - SSp
            correction_subsets.append(C)

            if hasattr(self, "matching_table") and self.verbose > 2:
                print("\nMCS \t = ", get_expl(self.matching_table, C))
            elif self.verbose > 2:
                print("\nMCS \t = ", C)

            # project the new correction subset on the useful literals of
            # the formula
            HS, HSp = HSp, (HSp | (A & C))

            # computing a new -- satisfiable! -- subset
            sat, SSp = self.subsetmax_sat(HSp, F, phases=I)

            if hasattr(self, "matching_table") and self.verbose > 2:
                print("\nSS \t= ", get_expl(self.matching_table, HS), "->", get_expl(self.matching_table, HSp), "->", get_expl(self.matching_table, SSp))
            elif self.verbose > 2:
                print("\nSS \t = ", HS, "->", HSp , "->", SSp)

        return correction_subsets

    def subsetmax_sat(self, S, F, phases=None):
        if phases==None:
            phases=self.Iend

        sat, SSp = self.checkSat(S, phases=phases)

        if not sat:
            return sat, S

        SS = set(SSp) & F

        remaining_to_check = F - SS
        # remaining_to_check.sorted(key=lambda x: 1 if (x in self.Iend) else 10)

        while(len(remaining_to_check) > 0):
            c = remaining_to_check.pop()
            set_c = set({c})
            sat, SSp = self.checkSat(SS | set_c, phases=phases)
            if sat:
                SS |= (SSp&F)

            remaining_to_check -= SS

        return True, SS

    def checkSat(self, Ap: set, phases=None, end_time_timeout=None):
        """Check satisfiability of given assignment of subset of the variables
        of Vocabulary V.
            - If the subset is unsatisfiable, Ap is returned.
            - If the subset is satisfiable, the model computed by the sat
                solver is returned.

        Args:
            Ap (set): Susbet of literals

        Returns:
            (bool, set): sat value, model assignment
        """
        if phases:
            self.sat_solver.set_phases(literals=phases)

        solved = self.sat_solver.solve_limited(assumptions=list(Ap), expect_interrupt=True)
        # print("user_Vars", self.U)
        if not solved:
            return solved, Ap

        model = set(self.sat_solver.get_model())
        return solved, model


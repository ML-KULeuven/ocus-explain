from .parameters import Assumptions, Grow, MCS, SMUSParams, STATS
from pysat.formula import CNF, WCNF
from pysat.examples.hitman import Hitman
from pysat.solvers import Solver
from pysat.examples.mcsls import MCSls
from pysat.examples.lbx import LBX


class SMUS(object):
    def __init__(self, params=SMUSParams(), from_file=None, from_clauses=None, from_cnf=None, benchmark=True):
        self.clauses = list()
        self.assumptions = set()
        params.checkparams()
        self.params = params
        self.ids = {}

        if from_file:
            self.import_file(from_file)
        elif from_clauses:
            self.import_clauses(from_clauses)
        elif from_cnf:
            self.import_cnf(from_cnf)

        if benchmark:
            self.stats = STATS()

    def import_file(self, from_file):
        cnf = CNF(from_file=from_file)
        if self.params.assumptions is Assumptions.BASE:
            self.ids = self.add_assumptions(cnf.clauses, cnf.nv)
        elif self.params.assumptions is Assumptions.OPT:
            self.ids = self.add_assumptions_opt(cnf.clauses, cnf.nv)

    def import_clauses(self, from_clauses):
        cnf = CNF(from_clauses=from_clauses)
        if self.params.assumptions is Assumptions.BASE:
            self.ids = self.add_assumptions(cnf.clauses, cnf.nv)
        elif self.params.assumptions is Assumptions.OPT:
            self.ids = self.add_assumptions_opt(cnf.clauses, cnf.nv)

    def import_cnf(self, cnf):
        # print(cnf.clauses)
        if self.params.assumptions is Assumptions.BASE:
            self.ids = self.add_assumptions(cnf.clauses, cnf.nv)
        elif self.params.assumptions is Assumptions.OPT:
            self.ids = self.add_assumptions_opt(cnf.clauses, cnf.nv)

    def add_assumptions(self, clauses, nv):
        bi_nv = nv + 1
        self.assumptions = set()
        ids = {}
        for id, clause in enumerate(clauses):
            new_clause = [-bi_nv] + clause
            self.clauses.append(new_clause)
            self.assumptions.add(bi_nv)
            ids[bi_nv]= id+1
            bi_nv += 1
        return ids

    def add_assumptions_opt(self, clauses, nv):
        bi_nv = CNF(from_clauses=clauses).nv + 1
        self.clauses = []
        self.assumptions = set(cl[0] for cl in clauses if len(cl) == 1)
        ids = {}

        for clause in clauses:
            if sum(1 if -lit in clause else 0 for lit in self.assumptions) > 1:
                self.assumptions -= set(lit for lit in self.assumptions if -lit in clause)

        neg_ass = set(-lit for lit in self.assumptions) | self.assumptions
        for clause in clauses:
            if len(set(clause).intersection(neg_ass)) == 0:
                new_clause = [-bi_nv] + clause
                self.clauses.append(new_clause)
                self.assumptions.add(bi_nv)
                neg_ass |= {-bi_nv, bi_nv}
                bi_nv += 1
        return ids

    def disjointMCSes(self):
        mcs_computer = None
        MCSes = []
        soft = [[l] for l in self.assumptions]
        wcnf = WCNF()
        wcnf.extend(self.clauses)
        wcnf.extend(soft, [1]*len(soft))

        if self.params.mcses is MCS.LBX:
            mcs_computer = LBX(wcnf, use_cld=True, solver_name='g3')
        if self.params.mcses is MCS.MCSLS:
            mcs_computer = MCSls(wcnf, use_cld=True, solver_name='g3')

        for mcs in mcs_computer.enumerate():
            # block mcs from being used
            mcs_computer.block(mcs)
            # ensure mcses are actually disjoint!
            for l in mcs:
                mcs_computer.block([l])
            MCSes.append([soft[idx-1][0] for idx in  mcs])
        return MCSes

    def grow(self, F, hs):
        # if self.params.grow is Grow.IGNORE:
        return F - hs

    def compute(self):
        H = []
        F = set(self.assumptions)
        hs, C = set(), set(F)

        hitman = None
        if not self.params.mcses is MCS.IGNORE:
            H = self.disjointMCSes()
            hitman = Hitman(bootstrap_with=H, htype='sorted')
            self.stats.n_mcses = len(H)
        else:
            hitman = Hitman(htype='sorted')
            hitman.hit(C)

        oracle = Solver(bootstrap_with=self.clauses)
        # whose soft clauses are extended with
        # selector literals stored in "sels"

        while(True):
            hs = set(hitman.get())
            self.stats.n_hs += 1
            self.stats.n_H  += 1

            if not oracle.solve(assumptions=list(hs)):
                oracle.delete()
                hitman.delete()
                self.stats.H = H
                return [self.ids[l] for l in hs]

            C = self.grow(F, hs)
            self.stats.n_grow +=1

            hitman.hit(C)


from pyexplain.solvers.params import OptUxParams
import time
from pyexplain.solvers.hittingSet import CondOptHS
from pysat.formula import CNF, WCNF
from pyexplain.solvers.optux import OptUx
from pyexplain.explain.csp_explain import CSPExplain

class OptUXExplain(CSPExplain):
    def __init__(self, C: CNF, params=OptUxParams(), verbose=True, matching_table=None):
        CSPExplain.__init__(self, C=C, verbose=verbose, matching_table=matching_table)
        # supplementary data
        self.time_statisitics["tavg_greedy_explain"] = []
        self.params = params

    def preprocess(self, U: set, f, I0: set, Iend: set):
        remaining = Iend-I0

        # Keeping track of weighted formula that can be incrementally built
        # hard clauses
        hard = self.cnf.clauses
        soft = [[l] for l in I0]
        soft_weight = [f(l) for l in I0]
        self.Iprev = set(I0)

        # Keeping track of the explanation costs
        self.best_costs = dict()
        self.best_expls = dict()
        self.softs = dict()

        # Explanataion variables
        self.I0 = I0
        self.Iend = Iend
        self.U = set(U) | set(-l for l in U)
        Xbest = I0 | {-l for l in  Iend - I0}
        f_xbest = sum(f(l) for l in Xbest)

        self.wcnf_dict = {l:WCNF() for l in Iend-I0}

        for l in Iend-I0:
            self.softs[l] = [[-l]] + soft
            # initialising the best cost
            self.best_costs[l] = f_xbest

            # keep previous solutions as well
            self.best_expls[l] = set(I0) | set({-l})

            # Hard is not going to change!
            self.wcnf_dict[l].extend(hard)
            # Soft lits will be extended in bestStep with new information
            # Less things to initialise!
            self.wcnf_dict[l].extend([[-l]] + soft, soft_weight+[1])

    def bestStep(self, f, Iend: set, I: set):
        """
        bestStep computes a subset A' of A that satisfies p s.t.
        C u A' is UNSAT and A' is f-optimal.

        Args:

            f (list): A cost function mapping 2^A -> N.
            Iend (set): The cautious consequence, the set of literals that hold in
                        all models.
            I (set): A partial interpretation such that I \subseteq Iend.
            sat (pysat.Solver): A SAT solver initialized with a CNF.
        """
        for i in I:
            if i in self.best_costs:
                del self.best_costs[i]
            if i in self.best_expls:
                del self.best_expls[i]
            if i in self.softs:
                del self.softs[i]
            if i in self.wcnf_dict:
                del self.wcnf_dict[i]

        remaining = list(Iend - I)
        disable_disjoint = self.params.disable_disjoint_mcses
        new_soft = [[l] for l in I - self.Iprev]
        new_weight = [f(l) for l in I - self.Iprev]

        best_lit = min(self.best_costs, key=self.best_costs.get)
        best_expl = set(self.best_expls[best_lit])
        best_cost = self.best_costs[best_lit]

        self.Iprev = set(I)
        t_greedyBestStep = []

        for id, l in enumerate(remaining):
            self.softs[l] += new_soft
            self.wcnf_dict[l].extend(new_soft, new_weight)

            expl, cost_expl, opt_mus_ids = None, 0, None
            # soft literatls for explanations

            # hard = constraints
            # soft = selectors and interpretation + (-literal)
            tbestStep = time.time()

            # compute optimal-MUS
            with OptUx(self.wcnf_dict[l], disable_dijsoint=disable_disjoint) as optux:
                opt_mus_ids = optux.compute()
                expl = set(self.softs[l][id-1][0] for id in opt_mus_ids)
                cost_expl = sum(f(l) for l in expl)

            t_greedyBestStep.append(time.time() - tbestStep)
            if cost_expl < self.best_costs[l]:
                self.best_costs[l] = cost_expl
                self.best_expls[l] = set(expl)
                # print(f"\t Explanation lit {l} improved!")

            # store explanation
            if cost_expl <= best_cost:
                best_expl = expl
                best_lit = l
                best_cost = cost_expl

        # literal already found, remove its cost
        del self.best_costs[best_lit]
        del self.best_expls[best_lit]
        del self.softs[best_lit]
        del self.wcnf_dict[best_lit]

        if self.verbose > 0:
            print('\t Average time to explanation=', round(sum(t_greedyBestStep)/len(t_greedyBestStep), 2), "s")

        # statistics
        self.time_statisitics["tavg_greedy_explain"].append(sum(t_greedyBestStep)/len(t_greedyBestStep))

        return best_expl


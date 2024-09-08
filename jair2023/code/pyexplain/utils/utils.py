from .exceptions import CostFunctionError
import itertools
from pysat.solvers import Solver

def flatten(ll):
    return [e for l in ll for e in l]

def add_assumptions(cnf):
    flat = set(abs(i) for lst in cnf for i in lst)
    max_lit = max(flat)

    cnf_ass = []
    assumptions = []
    for id, cl in enumerate(cnf):
        ass = max_lit + id + 1
        cl.append(-ass)
        assumptions.append(ass)
        cnf_ass.append(cl)

    return cnf_ass, assumptions


def get_user_vars(cnf):
    """Flattens cnf into list of different variables.

    Args:
        cnf (CNF): CNF object

    Returns:
        set: lits of variables present in cnf.
    """
    U = set(abs(l) for lst in cnf.clauses for l in lst)
    return U


def cost_puzzle(U, I, cost_clue):
    """
    U = user variables
    I = initial intepretation

    bij/trans/clues = subset of user variables w/ specific cost.
    """
    litsU = set(abs(l) for l in U) | set(-abs(l) for l in U)

    I0 = set(I)

    def cost_lit(lit):
        if lit not in litsU:
            raise CostFunctionError(U, lit)
        elif lit in cost_clue:
            return cost_clue[lit]
        else:
            # lit in
            return 1

    return cost_lit


def cost(U, I):
    litsU = set(abs(l) for l in U) | set(-abs(l) for l in U)
    I0 = set(I)

    def cost_lit(lit):
        if lit not in litsU:
            raise CostFunctionError(U, lit)
        elif lit in I0 or -lit in I0:
            return 20
        else:
            return 1

    return cost_lit

def get_expl(matching_table, Ibest, Nbest=None):
    if matching_table is None or Ibest is None:
        return str(Ibest)

    s = ""
    if not 'Transitivity constraint' in matching_table:
        matched_left_literals = []
        for i in Ibest:
            if i in matching_table:
                matched_left_literals.append(matching_table[i])
            else:
                matched_left_literals.append(str(i))
        s = ", ".join(matched_left_literals)

        if Nbest:
            s += " => "
            matched_right_literals = []
            for i in Nbest:
                if i in matching_table:
                    matched_right_literals.append(matching_table[i])
                else:
                    matched_right_literals.append(str(i))
            s += ", ".join(matched_right_literals)
    else:
        for i in Ibest:
            if(i in matching_table['Transitivity constraint']):
                s+= "trans: " + str(i) + "\n"
            elif(i in matching_table['Bijectivity']):
                s+= "bij: " + str(i) + "\n"
                print("bij", i)
            elif(i in matching_table['clues']):
                s+= "clues n°"+ matching_table['clues'][i] + "\n"
            else:
                s+= "Fact: " + str(i) + "\n"
    return s


def keep_largest_sublists(input_list):
    sets = [set(l) for l in input_list]

    return [l for l,s in zip(input_list, sets) if not any(s < other for other in sets)]


def pretty_print(list_of_clauses):
    for clauses in list_of_clauses:

        s = "\\{"
        s+= ", ".join(clauses)
        s+="\\}"
        print(s)

def keep_smallest_sublists(input_list):
    to_keep = []
    sets = [set(l) for l in input_list]
    for l,s in zip(input_list, sets):
        if not any(s > other for other in sets):
            to_keep.append(l)
    return to_keep

def extract_models_mcses_muses(clauses):
    all_mcses = []
    all_models = []
    all_muses = []
    for L in range(0, len(clauses)+1):
        for subset in itertools.combinations(clauses, L):

            with Solver(bootstrap_with=subset) as s:
                if not s.solve():
                    # print("MUS:", [f"c_{c1.index(si)+1}" for si in subset])
                    all_muses.append([f"c_{clauses.index(si)+1}" for si in subset])
                else:
                    # print("SAT:", [f"c_{c1.index(si)+1}" for si in subset])
                    all_models.append([f"c_{clauses.index(si)+1}" for si in subset])
                    # print("\t MCS", [f"c_{id+1}" for id, c in enumerate(c1) if c not in subset])
                    all_mcses.append([f"c_{id+1}" for id, c in enumerate(clauses) if c not in subset])

    mcses = keep_smallest_sublists(all_mcses)
    models = keep_largest_sublists(all_models)
    muses = keep_smallest_sublists(all_muses)

    return models, mcses, muses
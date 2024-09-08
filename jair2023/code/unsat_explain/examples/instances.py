from pysat.formula import CNF

def smus_assumptions():
    l = 1
    m = 2
    n = 3
    p = 4
    s = 5
    all_lits = [l,m,n,p,s]
    max_lit = max(all_lits)
    b = range(max_lit+1, max_lit+1 + 8)
    clauses = []
    clauses.append([-b[0], -s])    # c1: ¬s
    clauses.append([-b[1], s, -p]) # c2: s or ¬p
    clauses.append([-b[2], p])     # c3: p
    clauses.append([-b[3], -p, m]) # c4: ¬p or m
    clauses.append([-b[4], -m, n]) # c5: ¬m or n
    clauses.append([-b[5], -n])    # c6: ¬n
    clauses.append([-b[6], -m, l]) # c7 ¬m or l
    clauses.append([-b[7], -l])    # c8 ¬l
    
    matching_table = {
        l:"l",
        m:"m",
        n:"n",
        p:"p",
        s:"s",
        -l:"-l",
        -m:"-m",
        -n:"-n",
        -p:"-p",
        -s:"-s",
    }
    matching_table.update({lit:f"c_{{{id}}}" for id, lit in enumerate(b)})

    return {
        'clauses':clauses, 
        'vars': list(b)+all_lits,
        'assumptions': list(b),
        'matching_table': matching_table
        }


def smus_CNF():
    l = 1
    m = 2
    n = 3
    p = 4
    s = 5
    t = 6
    cnf = CNF()
    cnf.append([-s])    # c1: ¬s
    cnf.append([s, -p]) # c2: s or ¬p
    cnf.append([p])     # c3: p
    cnf.append([-p, m]) # c4: ¬p or m
    cnf.append([-m, n]) # c5: ¬m or n
    cnf.append([-n])    # c6: ¬n
    cnf.append([-m, l]) # c7 ¬m or l
    cnf.append([-l])    # c8 ¬l
    weights = [len(c)*5 for c in cnf.clauses]
    return cnf, weights

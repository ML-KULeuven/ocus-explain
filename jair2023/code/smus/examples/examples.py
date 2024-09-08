from pysat.formula import CNF, WCNF



def example_smus():
    l = 1
    m = 2
    n = 3
    p = 4
    s = 5
    cnf = CNF()
    cnf.append([-p, m]) # c4: ¬p or m
    cnf.append([-m, n]) # c5: ¬m or n
    cnf.append([-n])    # c6: ¬n
    cnf.append([-s])    # c1: ¬s
    cnf.append([-m, l]) # c7 ¬m or l
    cnf.append([-l])    # c8 ¬l
    cnf.append([s, -p]) # c2: s or ¬p
    cnf.append([p])     # c3: p

    return cnf

def example_bacchus():
    cnf = CNF()
    cnf.append([6, 2])    # c1: ¬s
    cnf.append([-6, 2])    # c1: ¬s
    cnf.append([-2, 1])    # c1: ¬s
    cnf.append([-1])    # c1: ¬s
    cnf.append([-6, 8])    # c1: ¬s
    cnf.append([6, 8])    # c1: ¬s
    cnf.append([2, 4])    # c1: ¬s
    cnf.append([-4, 5])    # c1: ¬s
    cnf.append([7, 5])    # c1: ¬s
    cnf.append([-7, 5])    # c1: ¬s
    cnf.append([-5, 3])    # c1: ¬s
    cnf.append([-3])    # c1: ¬s
    return cnf
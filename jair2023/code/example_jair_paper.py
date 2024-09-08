import pysat
import itertools
from pysat.solvers import Solver

c1 = [
    [ -1, -2 , 3], 
    [-1, 2, 3], 
    [-2, -3], 
    [1], 
    # [-3, -2], 
    [-1, 2], 
    [-1, -3]
]
all_mcses = []
all_models = []
all_muses = []

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


for L in range(0, len(c1)+1):
    for subset in itertools.combinations(c1, L):

        with Solver(bootstrap_with=subset) as s:
            if not s.solve():
                # print("MUS:", [f"c_{c1.index(si)+1}" for si in subset])
                all_muses.append([f"c_{c1.index(si)+1}" for si in subset])
            else:
                # print("SAT:", [f"c_{c1.index(si)+1}" for si in subset])
                all_models.append([f"c_{c1.index(si)+1}" for si in subset])
                # print("\t MCS", [f"c_{id+1}" for id, c in enumerate(c1) if c not in subset])
                all_mcses.append([f"c_{id+1}" for id, c in enumerate(c1) if c not in subset])

remaining_mcses = keep_smallest_sublists(all_mcses)
remaining_models = keep_largest_sublists(all_models)
remaining_muses = keep_smallest_sublists(all_muses)

# selected_ids = [0, 1, 3, 5]
# with Solver(bootstrap_with=[ci for id, ci in enumerate(c1) if id in selected_ids]) as s:
#     print(s.solve())
# print("all_models")
# print(all_models)
# print(remaining_models)


# print(all_mcses)
print("all_mcses")
pretty_print(remaining_mcses)

print("all_muses")
pretty_print(remaining_muses)

# print(all_muses)
# # c2 = [
#     [ -1, -2 , 3], 
#     [-1, 2, 3], 
#     [1], 
#     [-2, -3],
#     [-2],
#     [-3]
#     # [-1, 2], 
#     # [-1, -3]
# ]


# import itertools

# all_mcses = []
# all_models = []
# all_muses = []
# for L in range(0, len(c2)+1):
#     for subset in itertools.combinations(c2, L):

#         with Solver(bootstrap_with=subset) as s:
#             if not s.solve():
#                 print("MUS:", [f"c_{c2.index(si)+1}" for si in subset])
#                 all_muses.append([f"c_{c2.index(si)+1}" for si in subset])
#             else:
#                 print("SAT:", [f"c_{c2.index(si)+1}" for si in subset])
#                 all_models.append([f"c_{c2.index(si)+1}" for si in subset])
#                 print("\t MCS", [f"c_{id+1}" for id, c in enumerate(c2) if c not in subset])
#                 all_mcses.append([f"c_{c2.index(si)+1}" for si in subset])

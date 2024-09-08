from pyexplain.examples.sudoku import get_random_sudoku_grid
# explanation params
from pyexplain.solvers.params import COusParams, OUSParallelIncrNaiveParams
from pyexplain.solvers.params import DisjointMCSes, Grow

from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.explain.parallel_greedy_incr_naive_explain import ParallelGreedyIncrNaiveExplain

from pysat.formula import CNF

# CPPY modeling environment
from cppy import *
from cppy.model_tools.to_cnf import *

## SUDOKU instance
from pyexplain.examples.sudoku import model_sudoku_cppy

import numpy as np

## SAMPLE Strategy
## Strategy 1: Fill a column
fill_column_grid = np.array([
    [4, 1, 2, 3],
    [2, 3, 1, 0],
    [3, 2, 4, 1],
    [1, 4, 3, 2]
])



# ## Strategy 2: Fill a row
# fill_row_grid = np.array(
#     [[1, 3, 9, 8, 0, 6, 5, 2, 7],
#     [7, 4, 6, 2, 3, 5, 8, 1, 9],
#     [8, 2, 5, 9, 7, 1, 6, 3, 4],
#     [6, 5, 3, 7, 1, 8, 4, 9, 2],
#     [2, 9, 7, 3, 6, 4, 1, 5, 8],
#     [4, 8, 1, 5, 9, 2, 3, 7, 6],
#     [5, 6, 4, 1, 2, 7, 9, 8, 3],
#     [3, 7, 8, 4, 5, 9, 2, 6, 1],
#     [9, 1, 2, 6, 8, 3, 7, 4, 5]])


all_constraints, user_vars, I, f, puzzle, matching_table  = model_sudoku_cppy(fill_column_grid)

n = puzzle.shape[0]

for i in range(n):
    for j in range(n):
        for v in range(n):
            bv = puzzle[i, j, v].name + 1
            matching_table[bv] = f"{(v+1)} ({i+1},{j+1})"
            matching_table[-bv] = f"{-(v+1)} ({i+1},{j+1})"

params = OUSParallelIncrNaiveParams()
params.disjoint_mcses = DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY
params.grow = Grow.MAXSAT
ocus_expl_computer = ParallelGreedyIncrNaiveExplain(C=CNF(from_clauses=all_constraints), params=params, matching_table=matching_table, verbose=1)
expl_sequence = ocus_expl_computer.explain(U=user_vars, f=f, I0=I)


# ## Strategy 2: Fill a row
# fill_row_grid = np.array(
#     [[1, 3, 9, 8, 4, 6, 5, 2, 7],
#     [7, 4, 6, 2, 3, 5, 8, 1, 9],
#     [8, 2, 5, 9, 7, 1, 6, 3, 4],
#     [6, 5, 3, 7, 1, 8, 4, 9, 2],
#     [2, 9, 7, 3, 6, 4, 1, 5, 8],
#     [4, 8, 1, 5, 9, 2, 3, 7, 6],
#     [5, 6, 4, 1, 2, 7, 9, 8, 3],
#     [3, 7, 8, 4, 5, 9, 2, 6, 1],
#     [9, 1, 2, 6, 8, 3, 7, 4, 5]])

# all_constraints, user_vars, I, f, puzzle, matching_table  = model_sudoku_cppy(fill_row_grid)

# for i in range(9):
#     for j in range(9):
#         for v in range(9):
#             bv = puzzle[i, j, v].name + 1
#             matching_table[bv] = f"{(v+1)} ({i+1},{j+1})"
#             matching_table[-bv] = f"{-(v+1)} ({i+1},{j+1})"

# params = OUSParallelIncrNaiveParams()
# params.disjoint_mcses = DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY
# params.grow = Grow.MAXSAT
# ocus_expl_computer = ParallelGreedyIncrNaiveExplain(C=CNF(from_clauses=all_constraints), params=params, matching_table=matching_table, verbose=1)
# expl_sequence = ocus_expl_computer.explain(U=user_vars, f=f, I0=I)
# # all_constraints, user_vars, I, f, puzzle, matching_table = get_random_sudoku_grid()

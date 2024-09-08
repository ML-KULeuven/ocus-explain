import json
from pathlib import Path
from pyexplain.utils.utils import cost_puzzle, flatten
import numpy as np
import sys, os
import math
sys.path.insert(0, os.path.abspath('/home/emilio/research/CPMpy/'))
sys.path.insert(0, os.path.abspath('/data/brussel/101/vsc10143/cpmpy/'))

from cpmpy import *
from cpmpy.expressions.variables import *
from cpmpy.model import Model
from cpmpy.solvers.pysat import CPM_pysat
from cpmpy.transformations.to_cnf import to_cnf
import itertools
from pysat.solvers import Solver


def exactly_one(lst):
    # return sum(lst) == 1
    # (l1|l2|..|ln) & (-l1|-l2) & ...
    allpairs = [(~a|~b) for a, b in itertools.combinations(lst, 2)]
    return [any(lst)] + allpairs


# def int_model_sudoku(given):
#     n = len(given[0])

#     ## MODELING SUDOKU
#     # Variables
#     puzzle = intvar(1,n, shape=given.shape, name="puzzle")

#     sudoku_model = Model(
#         # Constraints on values (cells that are not empty)
#         puzzle[given!=e] == given[given!=e], # numpy's indexing, vectorized equality
#         [AllDifferent(row) for row in puzzle],
#         [AllDifferent(col) for col in puzzle.T]
#     )

#     reg = math.ceil(math.sqrt(n)) # size of region
#     for i in range(0, n, reg):
#         for j in range(0, n, reg):
#             sudoku_model += AllDifferent(puzzle[i:i+reg, j:j+reg]) # python's indexing

#     sudoku_boolmodel = BoolModel(int_model=sudoku_model, reify=True)

#     return puzzle, sudoku_boolmodel

def model_sudoku_cpmpy(grid):
    #print(grid)
    n = grid.shape[0]
    hardcons    = []
    softlits    = []
    pos_givens  = []
    neg_givens  = []

    ## variables (row, column, value)
    puzzle = boolvar(shape=(n, n, n))

    ## Givens
    for row in range(n):
        for col in range(n):
            if grid[row, col] > 0:
                # set value of number to true
                pos_givens += [puzzle[row, col, grid[row, col] - 1]]
                neg_givens  += [
                    ~puzzle[row, col, number] for number in range(n) if number != grid[row, col] - 1
                ]

    softlits += pos_givens + neg_givens
    ## CELL only 1 value possible
    bv = boolvar()
    cell_softs = [bv]
    softlits += cell_softs

    for row in range(n):
        for col in range(n):
            # 1 of them has to be true
            # adding to constraints
            hardcons += [bv.implies(cons) for cons in exactly_one(puzzle[row, col, :])]

    row_softs = []
    col_softs = []

    for row in range(n):
        bv_row = boolvar()
        bv_col = boolvar()

        ## ROW all different constraint
        hardcons += [bv_row.implies(cons) for number in range(n) for cons in exactly_one(puzzle[row, :, number])]
        ## COLUMN all different constraint
        hardcons += [bv_col.implies(cons) for number in range(n) for cons in exactly_one(puzzle[:, col, number])]

        row_softs += [bv_row]
        col_softs += [bv_col]

    softlits += row_softs + col_softs

    ## BLOCK all different constraint
    n_root = int(n**(1/2))
    block_soft = []
    for row in range(0, n, n_root):
        for col in range(0, n, n_root):
            bi_pos = boolvar()
            bi_neg = boolvar()


            cblock_pos = [
                any(puzzle[row:row+n_root,col:col+n_root,number].flat)
                for number in range(n)
            ]

            # ensure all different of all numbers
            cblock_neg = [
                (~puzzle[i1,j1,number] | ~puzzle[i2,j2,number])
                for number in range(n)
                for i1 in range(row,row+n_root)
                for i2 in range(row,row+n_root)
                for j1 in range(col,col+n_root)
                for j2 in range(col,col+n_root)
                if not(i1 == i2 and j1 == j2)
            ]

            hardcons += [bi_pos.implies(cons) for cons in cblock_pos]
            hardcons += [bi_neg.implies(cons) for cons in cblock_neg]

            block_soft += [bi_pos, bi_neg]

    ## CPMPY translatte
    pysat_model = CPM_pysat(Model(hardcons+softlits))
    all_constraints= pysat_model.make_cnf(Model(hardcons)).clauses

    ## use pysat_var
    I =set(pysat_model.pysat_var(cpm_var) for cpm_var in softlits)

    user_vars = set(abs(pysat_model.pysat_var(cpm_var)) for cpm_var in puzzle.flat ) | set(abs(l) for l in I)
    user_vars |= set(-l for l in user_vars)

    weighing = {}
    matching_table = {}

    ## TODO: add weights for literals of interpretation

    # bijectivities
    for softlit in cell_softs:
        weighing[pysat_model.pysat_var(softlit)]    = 60
        weighing[-pysat_model.pysat_var(softlit)]   = 60

    # all different constraints
    for softlit in block_soft + row_softs + col_softs:
        weighing[pysat_model.pysat_var(softlit)]    = 100
        weighing[-pysat_model.pysat_var(softlit)]   = 100


    f = cost_puzzle(user_vars, I, weighing)

    for id, softlit in enumerate(cell_softs):
        matching_table[pysat_model.pysat_var(softlit)] = f'CELL AllDiff [{str(id)}]'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'CELL AllDiff [{str(id)}]'

    for id, softlit in enumerate(row_softs):
        matching_table[pysat_model.pysat_var(softlit)] = f'ROW POS [{str(id+1)}] AllDiff'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'ROW POS [{str(id+1)}] AllDiff'

    for id, softlit in enumerate(col_softs):
        matching_table[pysat_model.pysat_var(softlit)] = f'ROW NEG [{str(id+1)}] AllDiff'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'ROW NEG [{str(id+1)}] AllDiff'


    for id, softlit in enumerate(block_soft):
        matching_table[pysat_model.pysat_var(softlit)] = f'COLUMN POS[{str(id+1)}] AllDiff'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'COLUMN POS[{str(id+1)}] AllDiff'

    return all_constraints, user_vars, I, f, puzzle, matching_table

def pickle_sudoku_cpmpy(grid, output_filename, instance_name='sudoku' ):
    n = grid.shape[0]
    hardcons    = []
    softlits    = []
    pos_givens  = []
    neg_givens  = []

    ## variables (row, column, value)
    puzzle = boolvar(shape=(n, n, n))

    ## Givens
    for row in range(n):
        for col in range(n):
            if grid[row, col] > 0:
                # set value of number to true
                pos_givens += [puzzle[row, col, grid[row, col] - 1]]
                neg_givens  += [
                    ~puzzle[row, col, number] for number in range(n) if number != grid[row, col] - 1
                ]

    softlits += pos_givens + neg_givens
    ## CELL only 1 value possible
    bv = boolvar()
    cell_softs = [bv]
    softlits += cell_softs

    for row in range(n):
        for col in range(n):
            # 1 of them has to be true
            # adding to constraints
            hardcons += [bv.implies(cons) for cons in exactly_one(puzzle[row, col, :])]

    row_softs = []
    col_softs = []

    for row in range(n):
        bv_row = boolvar()
        bv_col = boolvar()

        ## ROW all different constraint
        hardcons += [bv_row.implies(cons) for number in range(n) for cons in exactly_one(puzzle[row, :, number])]
        ## COLUMN all different constraint
        hardcons += [bv_col.implies(cons) for number in range(n) for cons in exactly_one(puzzle[:, col, number])]

        row_softs += [bv_row]
        col_softs += [bv_col]

    softlits += row_softs + col_softs

    ## BLOCK all different constraint
    n_root = int(n**(1/2))
    block_soft = []
    for row in range(0, n, n_root):
        for col in range(0, n, n_root):
            bi_pos = boolvar()
            bi_neg = boolvar()


            cblock_pos = [
                any(puzzle[row:row+n_root,col:col+n_root,number].flat)
                for number in range(n)
            ]

            # ensure all different of all numbers
            cblock_neg = [
                (~puzzle[i1,j1,number] | ~puzzle[i2,j2,number])
                for number in range(n)
                for i1 in range(row,row+n_root)
                for i2 in range(row,row+n_root)
                for j1 in range(col,col+n_root)
                for j2 in range(col,col+n_root)
                if not(i1 == i2 and j1 == j2)
            ]

            hardcons += [bi_pos.implies(cons) for cons in cblock_pos]
            hardcons += [bi_neg.implies(cons) for cons in cblock_neg]

            block_soft += [bi_pos, bi_neg]

    ## CPMPY translatte
    pysat_model = CPM_pysat(Model(hardcons+softlits))
    all_constraints= pysat_model.make_cnf(Model(hardcons)).clauses

    ## use pysat_var
    I =set(pysat_model.pysat_var(cpm_var) for cpm_var in softlits)

    user_vars = set(abs(pysat_model.pysat_var(cpm_var)) for cpm_var in puzzle.flat ) | set(abs(l) for l in I)
    user_vars |= set(-l for l in user_vars)

    weighing = {}
    matching_table = {}

    ## TODO: add weights for literals of interpretation

    # bijectivities
    for softlit in cell_softs:
        weighing[pysat_model.pysat_var(softlit)]    = 60
        weighing[-pysat_model.pysat_var(softlit)]   = 60

    # all different constraints
    for softlit in block_soft + row_softs + col_softs:
        weighing[pysat_model.pysat_var(softlit)]    = 100
        weighing[-pysat_model.pysat_var(softlit)]   = 100


    f = cost_puzzle(user_vars, I, weighing)

    for id, softlit in enumerate(cell_softs):
        matching_table[pysat_model.pysat_var(softlit)] = f'CELL AllDiff [{str(id)}]'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'CELL AllDiff [{str(id)}]'

    for id, softlit in enumerate(row_softs):
        matching_table[pysat_model.pysat_var(softlit)] = f'ROW POS [{str(id+1)}] AllDiff'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'ROW POS [{str(id+1)}] AllDiff'

    for id, softlit in enumerate(col_softs):
        matching_table[pysat_model.pysat_var(softlit)] = f'ROW NEG [{str(id+1)}] AllDiff'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'ROW NEG [{str(id+1)}] AllDiff'


    for id, softlit in enumerate(block_soft):
        matching_table[pysat_model.pysat_var(softlit)] = f'COLUMN POS[{str(id+1)}] AllDiff'
        matching_table[-(pysat_model.pysat_var(softlit))] = f'COLUMN POS[{str(id+1)}] AllDiff'

    data = {
        'cnf': all_constraints,
        'assumption': list(I),
        'user_vars': list(user_vars),
        'name': instance_name,
        'weights': weighing
    }

    with Path(output_filename).open('w+') as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    # e = 0

    # given_4x4 = np.array([
    #     [4, 1, 2, 3],
    #     [2, 3, 1, e],
    #     [3, 2, e, 1],
    #     [1, e, 3, 2]
    # ])
    # puzzle_vars, sudoku_bool_model = int_model_sudoku(given_4x4)
    # print("puzzle_vars=", puzzle_vars)
    # print("reification_vars=", sudoku_bool_model.reification_vars)
    # # print(sudoku_bool_model.constraints)
    # print(sudoku_bool_model)
    pass

    # e = 0 # value for empty cells
    # given_9x9 = np.array([
    #     [e, e, e,  2, e, 5,  e, e, e],
    #     [e, 9, e,  e, e, e,  7, 3, e],
    #     [e, e, 2,  e, e, 9,  e, 6, e],

    #     [2, e, e,  e, e, e,  4, e, 9],
    #     [e, e, e,  e, 7, e,  e, e, e],
    #     [6, e, 9,  e, e, e,  e, e, 1],

    #     [e, 8, e,  4, e, e,  1, e, e],
    #     [e, 6, 3,  e, e, e,  e, 8, e],
    #     [e, e, e,  6, e, 8,  e, e, e]])

    # model_sudoku(given_9x9)

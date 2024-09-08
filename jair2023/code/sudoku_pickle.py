#!/usr/bin/env python3
import json
from pathlib import Path
from pyexplain.examples.utils import csv_to_numpy_grids

from pyexplain.examples.sudoku_cpmpy import pickle_sudoku_cpmpy



def pickle_all_sudokus(sudoku_grids, output_folder, base_filename,n=100):
    print("\n")
    for id, grid in enumerate(sudoku_grids[:n]):
        print(f"[{id+1}/{len(sudoku_grids)}]", flush=True, end='\r')
        output_filename = output_folder + base_filename + "_" + str(id) + '.json'
        pickle_sudoku_cpmpy(grid["puzzle"], output_filename, instance_name='sudoku')



if __name__ == "__main__":
    PATH_SUDOKU_PICKLES = "/home/emilio/research/OCUSExplain/code/pyexplain/examples/sudoku/pickles/"
    sudoku_grids_9x9_easy = csv_to_numpy_grids("/home/emilio/research/OCUSExplain/code/pyexplain/examples/sudoku/easy_sudokus.csv", difficulty=None)
    sudoku_grids_9x9_expert = csv_to_numpy_grids("/home/emilio/research/OCUSExplain/code/pyexplain/examples/sudoku/expert_sudokus.csv", difficulty=None)
    sudoku_grids_9x9_intermediate = csv_to_numpy_grids("/home/emilio/research/OCUSExplain/code/pyexplain/examples/sudoku/intermediate_sudokus.csv", difficulty=None)
    sudoku_grids_9x9_simple = csv_to_numpy_grids("/home/emilio/research/OCUSExplain/code/pyexplain/examples/sudoku/simple_sudokus.csv", difficulty=None)
    pickle_all_sudokus(sudoku_grids_9x9_easy, PATH_SUDOKU_PICKLES, "sudoku-easy")
    pickle_all_sudokus(sudoku_grids_9x9_expert, PATH_SUDOKU_PICKLES, "sudoku-expert")
    pickle_all_sudokus(sudoku_grids_9x9_intermediate, PATH_SUDOKU_PICKLES, "sudoku-intermediate")
    pickle_all_sudokus(sudoku_grids_9x9_simple, PATH_SUDOKU_PICKLES, "sudoku-simple")

    # sudoku_grids_25x25 = csv_to_numpy_grids("/Users/emiliogamba/Documents/GitHub/OCUSExplanations/code/pyexplain/examples/sudoku/25x25.csv", difficulty=None)
    # pickle_all_sudokus(sudoku_grids_25x25, PATH_SUDOKU_PICKLES, "25x25")

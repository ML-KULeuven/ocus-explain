#!/usr/bin/env python3
import argparse
from pathlib import Path

from pyexplain.examples.utils import from_json_pickle, sudoku_from_json_pickle
import time
from pyexplain.explain.ocus_non_incr_explain import OCUSExplainNotIncremental
from pyexplain.explain.ocus_non_incr_hs_explain import OCUSExplainNotIncrementalHS
from pyexplain.utils.utils import cost_puzzle
from pyexplain.solvers.params import COusNonIncrParams, COusNonIncrHSParams
from pyexplain.examples.frietkot import frietKotProblem, originProblem, pastaPuzzle, p12, p13, p16, p18, p19,p20, p25, p93, simpleProblem

from pysat.formula import CNF

puzzle_funs = {
    "origin-problem": originProblem,
    "pastaPuzzle": pastaPuzzle,
    "p12": p12,
    "p13": p13,
    "p16": p16,
    "p18": p18,
    "p25": p25,
    "p20": p20,
    "p93": p93,
    "p19": p19,
    "frietkot": frietKotProblem,
    "simple": simpleProblem
}

p_clauses, p_ass, p_weights, p_user_vars, matching_table = None, None, None, None, None
time_start_setup = time.time()
# puzzle instance to test

output_folder = "/Users/emiliogamba/Documents/01_VUB/01_Research/01_Shared_Projects/05_OCUS_Explain/notebooks/journal/2021_jair_reviewing_data/"

for puzzle, puzzleFun in puzzle_funs.items():

    ocus_not_incr_params = COusNonIncrParams()
    ocus_not_incr_params.load_best_params()
    ocus_not_incr_params.output = output_folder + f"ocus_not_incr_{puzzle}.json"
    ocus_not_incr_params.instance = puzzle

    ocus_not_incr_hs_params = COusNonIncrHSParams()
    ocus_not_incr_hs_params.load_best_params()
    ocus_not_incr_hs_params.instance = puzzle
    ocus_not_incr_hs_params.output = output_folder + f"ocus_not_incr_hs_{puzzle}.json"

    # getting the clauses and weights
    p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()

    # User vocabulary
    n_expls = 50

    U = p_user_vars | set(x for lst in p_ass for x in lst)
    subset_p_user_vars = set(u for cnt, u in enumerate(p_user_vars) if cnt < n_expls)

    subset_u = subset_p_user_vars | set(x for lst in p_ass for x in lst)

    # initial interpretation
    I = set(x for lst in p_ass for x in lst)

    # weight/cost of explanations
    f = cost_puzzle(U, I, p_weights)

    # transform to CNF object
    #print("time_start_setup=", time.time() - time_start_setup)
    time_cnf = time.time()
    o_cnf = CNF(from_clauses=p_clauses)
    # print("time_cnf=", time.time() - time_cnf)

    # Optimal explanations
    ocus_not_incr_expl_computer = OCUSExplainNotIncremental(C=o_cnf,params=ocus_not_incr_params)
    ocus_not_incr_hs_computer = OCUSExplainNotIncrementalHS(C=o_cnf,params=ocus_not_incr_hs_params)

    # # only handling timeout error!
    # print("Running COUS explanations ")
    t_start_explain_cous = time.time()
    ocus_not_incr_expl_sequence = ocus_not_incr_expl_computer.explain(U=set(subset_u), f=f, I0=set(I))
    ocus_not_incr_expl_computer.export_statistics(ocus_not_incr_params, ocus_not_incr_params.output)
    print("Total Time COUS explanations:\n\t", round(time.time() - t_start_explain_cous, 2), "s")

    # print("Running COUS not incr HS explanations ")
    t_start_explain_cous_not_incr_hs = time.time()
    ocus_not_incr_hs_expl_sequence = ocus_not_incr_hs_computer.explain(U=set(subset_u), f=f, I0=set(I))
    ocus_not_incr_hs_computer.export_statistics(ocus_not_incr_hs_params, ocus_not_incr_hs_params.output)
    print("Total Time COUS not incr HS explanations:\n\t", round(time.time() - t_start_explain_cous_not_incr_hs, 2), "s")
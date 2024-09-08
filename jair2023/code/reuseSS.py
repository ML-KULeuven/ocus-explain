#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
import threading
import traceback

from pyexplain.examples.utils import from_json_pickle, sudoku_from_json_pickle
from pyexplain.explain.ocus_explain_subsets import OCUSExplainSubsets
from pyexplain.explain.ocus_non_incr_hs_explain import OCUSExplainNotIncrementalHS
from pyexplain.explain.parallel_greedy_incr_naive_explain import ParallelGreedyIncrNaiveExplain
from pyexplain.explain.greedy_noopt_explain import GreedyNoOptExplain
import time
from pyexplain.explain.ocus_non_incr_explain import OCUSExplainNotIncremental
from pyexplain.explain.greedy_incr_shared_explain import GreedyIncrSharedExplain
from pyexplain.explain.greedy_incr_naive_explain import GreedyIncrNaiveExplain
from pyexplain.explain.greedy_explain import GreedyExplain
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.explain.mus_explain import MUSExplain
from pyexplain.explain.parallel_greedy_naive_explain import ParallelGreedyNaiveExplain
from pyexplain.utils.utils import cost_puzzle
from pyexplain.solvers.params import BestStepParams, COusNonIncrHSParams, COusNonIncrParams, COusParams, COusSubsetParams, DisjointMCSes, ExplanationComputer, Grow, Interpretation, MUSParams, OUSParallelIncrNaiveParams, OUSParallelNaiveParams, OptUxParams, OusIncrNaiveParams, OusIncrSharedParams, OusNoOptParams, OusParams, Weighing
from pyexplain.examples.frietkot import frietKotProblem, originProblem, pastaPuzzle, p12, p13, p16, p18, p19,p20, p25, p93, simpleProblem

from pysat.formula import CNF

import signal

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
DEMISTIFY_FOLDER = "pyexplain/examples/demistify/pickles/"
SUDOKU_FOLDER = "pyexplain/examples/sudoku/pickles/"

def timeoutHandler(signum, frame):
    raise TimeoutError()

def runpuzzle(params, verbose=False):
    assert isinstance(params, (COusParams, COusSubsetParams, COusNonIncrParams, COusNonIncrHSParams,OusNoOptParams, OusIncrNaiveParams, OusIncrSharedParams, OusParams, MUSParams, OUSParallelIncrNaiveParams, OUSParallelNaiveParams)), f"Wrong type of parameters= {type(params)}"
    p_clauses, p_ass, p_weights, p_user_vars, matching_table = None, None, None, None, None
    time_start_setup = time.time()
    # puzzle instance to test
    if params.instance in puzzle_funs:
        puzzleFun = puzzle_funs[params.instance]

        # getting the clauses and weights
        p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()

        # User vocabulary
        U = p_user_vars | set(x for lst in p_ass for x in lst)

        # initial interpretation
        I = set(x for lst in p_ass for x in lst)

        # weight/cost of explanations
        f = cost_puzzle(U, I, p_weights)
    elif params.instance in [f.name for f in Path(DEMISTIFY_FOLDER).iterdir() if f.is_file() and f.name.endswith(".json")]:
        _, _, p_clauses, p_ass, p_user_vars, p_weights = from_json_pickle(DEMISTIFY_FOLDER + params.instance)

        # User vocabulary
        U = set(p_user_vars) | set(x for lst in p_ass for x in lst)

        # initial interpretation
        I = set(x for lst in p_ass for x in lst)

        # weight/cost of explanations
        f = cost_puzzle(U, I, p_weights)
    elif params.instance.startswith('sudoku') and params.instance.endswith('.json'):
        _, p_clauses, U, I, p_weights = sudoku_from_json_pickle(SUDOKU_FOLDER + params.instance)

        f = cost_puzzle(U, I, p_weights)

    elif 'sudoku' in params.instance and not params.instance.endswith('.json'):
        from pyexplain.examples.utils import get_sudoku_grid
        from pyexplain.examples.sudoku_cpmpy import model_sudoku_cpmpy
        # get the grid from difficulty and index
        puzzle_grid = get_sudoku_grid(params.instance)
        assert puzzle_grid is not None, "Puzzle can't be run!"

        # clauses/weights of problem
        p_clauses, U, I, f, _, _  = model_sudoku_cpmpy(puzzle_grid)
    else:
        raise Exception("Puzzle not found!")

    # transform to CNF object
    print("time_start_setup=", time.time() - time_start_setup)
    time_cnf = time.time()
    o_cnf = CNF(from_clauses=p_clauses)
    print("time_cnf=", time.time() - time_cnf)

    expl_computer = None

    time_expl_computer = time.time()
    # verbose=3
    # Optimal explanations
    if isinstance(params, COusParams):
        expl_computer = OCUSExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    if isinstance(params, COusSubsetParams):
        expl_computer = OCUSExplainSubsets(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, COusNonIncrParams):
        expl_computer = OCUSExplainNotIncremental(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, COusNonIncrHSParams):
        expl_computer = OCUSExplainNotIncrementalHS(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, OusIncrNaiveParams):
        expl_computer = GreedyIncrNaiveExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, OusIncrSharedParams):
        expl_computer = GreedyIncrSharedExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, OusParams):
        expl_computer = GreedyExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, MUSParams):
        expl_computer = MUSExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, OusNoOptParams):
        expl_computer = GreedyNoOptExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, OUSParallelIncrNaiveParams):
        expl_computer = ParallelGreedyIncrNaiveExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)
    elif isinstance(params, OUSParallelNaiveParams):
        expl_computer = ParallelGreedyNaiveExplain(o_cnf, params=params, verbose=verbose, matching_table=matching_table)

    print("time_expl_computer=", time.time() - time_expl_computer)

    tstart = time.time()
    is_error=False
    try:
        expl_computer.time_statisitics["totalTime"] = expl_computer.params.timeout
        expl_computer.time_statisitics["timedout"] = True

        expl_computer.export_statistics(params=params, fname=params.output)

        if params.timeout:
            print("Starting timeout")
            _ = signal.signal(signal.SIGALRM, timeoutHandler)
            signal.alarm(params.timeout)
        # only handling timeout error!
        print("Starting explanations")
        if params.timeout:
            E = expl_computer.explain(U=U, f=f, I0=I, end_time_timeout=tstart + params.timeout, params=params, fname=params.output)
        else:
            E = expl_computer.explain(U=U, f=f, I0=I)
    except TimeoutError:
        print("Timeout error/Exception!")
        is_error=True
    except Exception as e:
        is_error=True
        print("Another Exception!", e)
        print(traceback.format_exc())
    finally:
        if params.timeout:
            print('signal 0')
            signal.alarm(0)

    print("Here!")
    expl_computer.time_statisitics["totalTime"] = round(time.time() - tstart)
    if (time.time() >= (tstart + params.timeout)) or is_error:
        expl_computer.time_statisitics["timedout"] = True
    else:
        expl_computer.time_statisitics["timedout"] = False

    twrite = time.time()
    expl_computer.export_statistics(params=params, fname=params.output)
    print("time_expl_computer=", time.time() - twrite)
    os._exit(0)


def argsToParams(args):
    """
    RQ1. implementation of Reuse of Satisfiable subsets for ous incremental
    in similar way to ocus incremental.
    """
    param_explanation_computer = {
        ExplanationComputer.MUS.name: MUSParams,
        ExplanationComputer.OUS_NO_OPT.name: OusNoOptParams,
        ExplanationComputer.OUS_SS.name: OusParams,
        ExplanationComputer.OUS_INCREMENTAL_NAIVE.name: OusIncrNaiveParams,
        ExplanationComputer.OUS_INCREMENTAL_SHARED.name: OusIncrSharedParams,
        ExplanationComputer.OUS_INCREMENTAL_NAIVE_PARALLEL.name: OUSParallelIncrNaiveParams,
        ExplanationComputer.OUS_NAIVE_PARALLEL.name: OUSParallelNaiveParams,
        ExplanationComputer.OCUS.name: COusParams,
        ExplanationComputer.OCUS_NOT_INCREMENTAL.name: COusNonIncrParams,
        ExplanationComputer.OCUS_NOT_INCREMENTAL_HS.name: COusNonIncrHSParams,
        ExplanationComputer.OCUS_SUBSETS.name: COusSubsetParams
    }

    if args.explanation_computer not in param_explanation_computer:
        raise Exception(f"Wrong params {str(args)}")

    params = param_explanation_computer[args.explanation_computer]()

    if args.maxsatpolarity and args.maxsatpolarity != "ignore":
        params.maxsat_polarity =  True if args.maxsatpolarity == "True" else False

    if args.grow and args.grow != "ignore":
        params.grow = Grow(args.grow)

    if args.interpretation  and args.interpretation != "ignore":
        params.interpretation = Interpretation(args.interpretation)

    if args.weighing and args.weighing != "ignore":
        params.maxsat_weighing = Weighing(args.weighing)

    if args.puzzle  and args.puzzle != "ignore":
        params.instance = args.puzzle

    if args.instance  and args.instance != "ignore":
        params.instance = args.instance

    if args.output  and args.output != "ignore":
        params.output = args.output

    if args.sort_literals and args.sort_literals != "ignore":
        params.sort_literals = True if  args.sort_literals == "True" else False

    if args.reuse_SSes and isinstance(params, BestStepParams) and args.reuse_SSes != "ignore":
        params.reuse_SSes =  True if args.reuse_SSes == "True" else False

    if args.timeout and args.timeout != "ignore":
        params.timeout = int(args.timeout)

    if args.disable_disjoint_mcses and args.disable_disjoint_mcses != "ignore":
        params.disable_disjoint_mcses =  True if args.disable_disjoint_mcses == "True" else False

    if args.disjoint_mcses and args.disjoint_mcses != "ignore":
        params.disjoint_mcses =  DisjointMCSes(args.disjoint_mcses)

    if args.disjoint_mcs_interpretation and args.disjoint_mcs_interpretation != "ignore":
        params.disjoint_mcs_interpretation =  Interpretation(args.disjoint_mcs_interpretation)

    if args.disjoint_mcs_weighing and args.disjoint_mcs_weighing != "ignore":
        params.disjoint_mcs_weighing =  Weighing(args.disjoint_mcs_weighing)

    return params

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Specify output file")
    parser.add_argument("-v", "--verbose", help="Verbosity.", nargs='?', const=0, type=int, default=0)
    parser.add_argument("-p", "--puzzle", help="Selected puzzle.")
    parser.add_argument("--instance", help="Selected instance.")
    parser.add_argument("-e", "--explanation_computer", help=f"Choose one ({list(ExplanationComputer)})")
    parser.add_argument("-r", "--reuse_SSes", help="Reuse of satisfiable subsets")
    parser.add_argument("-m", "--maxsatpolarity", help="Provide MaxSAT solver with polarities")
    parser.add_argument("-s", "--sort_literals", help="Sort the ltierals")
    parser.add_argument("-g", "--grow", help="Grow extension. Available values : [sat, subsetmax, maxsat]")
    parser.add_argument("-i", "--interpretation", help="Interpretation used in grow: [initial, actual, full]")
    parser.add_argument("-w", "--weighing", help="Weighing scheme of MaxSAT solver")
    parser.add_argument("-t", "--timeout", help="Timeout of explanations")
    parser.add_argument("-d", "--disable_disjoint_mcses", help="Disable disjoint MCSes for OPTUX-based explanations")
    parser.add_argument("--disjoint_mcses", help="Enable disjoint_mcses for OUS/OCUS")
    parser.add_argument("--disjoint_mcs_interpretation", help="Which interpretation to use on disjoint mcs")
    parser.add_argument("--disjoint_mcs_weighing", help="Which weighing scheme to use on disjoint mcs")

    args = parser.parse_args()
    params = argsToParams(args)
    runpuzzle(params, args.verbose)
    print("Finished running!")
    
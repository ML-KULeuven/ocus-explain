#!/usr/bin/env python3
import argparse
from pathlib import Path

from pyexplain.examples.utils import from_json_pickle, sudoku_from_json_pickle
import time
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.explain.mus_explain import MUSExplain
from pyexplain.utils.utils import cost_puzzle
from pyexplain.solvers.params import BestStepParams, COusNonIncrParams, COusParams, COusSubsetParams, DisjointMCSes, ExplanationComputer, Grow, Interpretation, MUSParams, OUSParallelIncrNaiveParams, OUSParallelNaiveParams, OusIncrNaiveParams, OusIncrSharedParams, OusNoOptParams, OusParams, Weighing
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
    assert isinstance(params, (COusParams, COusSubsetParams, COusNonIncrParams,OusNoOptParams, OusIncrNaiveParams, OusIncrSharedParams, OusParams, MUSParams, OUSParallelIncrNaiveParams, OUSParallelNaiveParams)), f"Wrong type of parameters= {type(params)}"
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
        p_weights = {k: 60 for k in p_weights.keys()}

        # User vocabulary
        U = set(p_user_vars) | set(x for lst in p_ass for x in lst)

        # initial interpretation
        I = set(x for lst in p_ass for x in lst)

        # weight/cost of explanations
        f = cost_puzzle(U, I, p_weights)
    elif params.instance.startswith('sudoku') and params.instance.endswith('.json'):
        _, p_clauses, U, I, p_weights = sudoku_from_json_pickle(SUDOKU_FOLDER + params.instance)
        p_weights = {k: 60 for k in p_weights.keys()}

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

    # Optimal explanations
    params.output = params.output.replace('.json', '_COUS.json')
    ocus_expl_computer = OCUSExplain(C=o_cnf,params=params)

    mus_params = MUSParams()
    mus_params.instance = params.instance
    mus_params.output = params.output.replace('_COUS', '_MUS')

    mus_expl_computer = MUSExplain(C=o_cnf,params=mus_params)

    # only handling timeout error!
    ocus_expl_sequence = ocus_expl_computer.explain(U=set(U), f=f, I0=set(I))
    _ = mus_expl_computer.explain(U=set(U), f=f, I0=set(I), prev_expl_seq=ocus_expl_sequence)

    ocus_expl_computer.export_statistics(params, params.output)
    mus_expl_computer.export_statistics(mus_params, mus_params.output)


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
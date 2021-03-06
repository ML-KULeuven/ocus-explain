#!/usr/bin/env python3

import time
from pyexplain.explain.ocus_non_incr_explain import OCUSExplainNotIncremental
from pyexplain.explain.greedy_incr_shared_explain import GreedyIncrSharedExplain
from pyexplain.explain.greedy_incr_naive_explain import GreedyIncrNaiveExplain
from pyexplain.explain.greedy_explain import GreedyExplain
from pyexplain.explain.ocus_explain import OCUSExplain
from pyexplain.explain.mus_explain import MUSExplain
from pyexplain.utils.utils import cost_puzzle
from pyexplain.solvers.params import BestStepParams, COusNonIncrParams, COusParams, ExplanationComputer, Grow, Interpretation, MUSParams, OusIncrNaiveParams, OusIncrSharedParams, OusParams, Weighing
import argparse
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


def timeoutHandler(signum, frame):
    raise TimeoutError()


def runpuzzle(params):
    assert isinstance(params, (COusParams, COusNonIncrParams, OusIncrNaiveParams, OusIncrSharedParams, OusParams, MUSParams)), f"Wrong type of parameters= {type(params)}"

    # puzzle instance to test
    puzzleFun = puzzle_funs[params.instance]

    # getting the clauses and weights
    p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzleFun()

    # transform to CNF object
    o_cnf = CNF(from_clauses=p_clauses)

    # User vocabulary
    U = p_user_vars | set(x for lst in p_ass for x in lst)

    # initial interpretation
    I = set(x for lst in p_ass for x in lst)

    # weight/cost of explanations
    f = cost_puzzle(U, I, p_weights)
    expl_computer = None

    # Optimal explanations
    if isinstance(params, COusParams):
        expl_computer = OCUSExplain(o_cnf, params=params, verbose=False)
    elif isinstance(params, COusNonIncrParams):
        expl_computer = OCUSExplainNotIncremental(o_cnf, params=params, verbose=False)
    elif isinstance(params, OusIncrNaiveParams):
        expl_computer = GreedyIncrNaiveExplain(o_cnf, params=params, verbose=False)
    elif isinstance(params, OusIncrSharedParams):
        expl_computer = GreedyIncrSharedExplain(o_cnf, params=params, verbose=False)
    elif isinstance(params, OusParams):
        expl_computer = GreedyExplain(o_cnf, params=params, verbose=False)
    elif isinstance(params, MUSParams):
        expl_computer = MUSExplain(o_cnf, params=params, verbose=False)

    tstart = time.time()
    try:
        _ = signal.signal(signal.SIGALRM, timeoutHandler)
        if params.timeout:
            signal.alarm(params.timeout)
        # only handling timeout error!
        expl_computer.explain(U=U, f=f, I0=I)
    except TimeoutError:
        expl_computer.time_statisitics["totalTime"] = expl_computer.params.timeout
        expl_computer.time_statisitics["timedout"] = True
    except Exception:
        expl_computer.time_statisitics["totalTime"] = round(time.time() - tstart)
        expl_computer.time_statisitics["timedout"] = True
    finally:
        if params.timeout:
            signal.alarm(0)

        expl_computer.export_statistics(params=params, fname=params.output)


def argsToParams(args):
    """
    """
    if args.explanation_computer == ExplanationComputer.MUS.name:
        params = MUSParams()
    elif args.explanation_computer == ExplanationComputer.OUS_INCREMENTAL_NAIVE.name:
        params = OusIncrNaiveParams()
    elif args.explanation_computer == ExplanationComputer.OUS_INCREMENTAL_SHARED.name:
        params = OusIncrSharedParams()
    elif args.explanation_computer == ExplanationComputer.OUS_SS.name:
        params = OusParams()
    elif args.explanation_computer == ExplanationComputer.OCUS.name:
        params = COusParams()
    elif args.explanation_computer == ExplanationComputer.OCUS_NOT_INCREMENTAL.name:
        params = COusNonIncrParams()
    else:
        raise Exception(f"Wrong params {str(args)}")
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

    if args.output  and args.output != "ignore":
        params.output = args.output

    if args.sort_literals and args.sort_literals != "ignore":
        params.sort_literals = True if  args.sort_literals == "True" else False

    if args.reuseSubset and isinstance(params, BestStepParams) and args.reuseSubset != "ignore":
        params.reuse_SSes =  True if args.reuseSubset == "True" else False

    if args.timeout and args.timeout != "ignore":
        params.timeout = int(args.timeout)

    if args.disable_disjoint_mcses and args.disable_disjoint_mcses != "ignore":
        params.disable_disjoint_mcses =  True if args.disable_disjoint_mcses == "True" else False

    return params

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Specify output file")
    parser.add_argument("-p", "--puzzle", help="Selected puzzle.")
    parser.add_argument("-e", "--explanation_computer", help=f"Choose one ({list(ExplanationComputer)})")
    parser.add_argument("-r", "--reuseSubset", help="Reuse of satisfiable subsets")
    parser.add_argument("-m", "--maxsatpolarity", help="Provide MaxSAT solver with polarities")
    parser.add_argument("-s", "--sort_literals", help="Sort the ltierals")
    parser.add_argument("-g", "--grow", help="Grow extension. Available values : [sat, subsetmax, maxsat]")
    parser.add_argument("-i", "--interpretation", help="Interpretation used in grow: [initial, actual, full]")
    parser.add_argument("-w", "--weighing", help="Weighing scheme of MaxSAT solver")
    parser.add_argument("-t", "--timeout", help="Timeout of explanations")
    parser.add_argument("-d", "--disable_disjoint_mcses", help="Disable disjoint MCSes for OPTUX-based explanations")

    args = parser.parse_args()
    params = argsToParams(args)
    runpuzzle(params)

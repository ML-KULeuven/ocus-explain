#!/usr/bin/env python3

import csv
from pathlib import Path
from pyexplain.examples.frietkot import frietKotProblem, originProblem, pastaPuzzle, p12, p13, p16, p18, p19,p20, p25, p93, simpleProblem
from pyexplain.solvers.params import BestStepParams, COusNonIncrParams, COusParams, Grow, Interpretation, MUSParams, OusIncrNaiveParams, OusIncrSharedParams, OusParams, Weighing
from datetime import datetime

SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAY = 24 * HOURS

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

def to_csv(params, fname):
    fieldnames= [
        # puzzle to explain
        "instance",
        # output file
        "output",
        # constrained = add additional constraint on lit to explain
        # incremental = reuse of Satisfiable subsets identically to
        # constrained OUS
        # incremental = reuse of Satisfiable subsets
        "explanation_computer",
        "reuse_SSes",
        # sort the literals to generate explanations
        "sort_literals",
        # execution parameters
        "grow",
        "interpretation",
        "maxsatpolarity",
        "weighing",
        "timeout"
    ]

    p = Path(fname)
    with open(fname, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for param in params:
            param_dict = param.to_dict()
            for k,v in param_dict.items():
                if v is None or v == "":
                    param_dict[k] = "ignore"
            writer.writerow(param_dict)


def generate_all_parameters(output_folder):
    allCOusParams = COusParamsSS(output_folder)
    allCOusNonIncrParams = COusNonIncrParamsSS(output_folder)
    allOusIncrNaiveParams = OusIncrNaiveParamsSS(output_folder)
    allOusIncrSharedParams = OusIncrSharedParamsSS(output_folder)
    allOusParams = OusParamsSS(output_folder)
    allMUSParams = MUSParamsSS(output_folder)

    all_params = []
    all_params += allCOusParams
    all_params += allCOusNonIncrParams
    all_params += allOusIncrNaiveParams
    all_params += allOusIncrSharedParams
    all_params += allOusParams
    all_params += allMUSParams

    return all_params


def all_params_to_files(input_folder, output_folder, params_fname):
    all_params = generate_all_parameters(output_folder)
    all_params_to_csv(params_fname, input_folder)

    if not Path(input_folder).exists():
        Path(input_folder).mkdir()

    bash_file = Path(input_folder) / "run_experiments.sh"
    script = ["#!/bin/bash -l",""]

    for id, param in enumerate(all_params):
        script.append(params_to_python_exec(param))

    with bash_file.open('w+') as fp:
        fp.writelines(map(lambda x: x+"\n", script))


def params_to_python_exec(params: BestStepParams):

    param_dict = params.to_dict()
    for k,v in param_dict.items():
        if v is None or v == "":
            param_dict[k] = "ignore"

    PBS_script = f"""python3 run_puzzle.py --output {param_dict["output"]} --puzzle {param_dict["instance"]} --explanation_computer {param_dict["explanation_computer"]} --reuseSubset {param_dict["reuse_SSes"]} --maxsatpolarity {param_dict["maxsatpolarity"]} --sort_literals {param_dict["sort_literals"]} --grow {param_dict["grow"]} --interpretation {param_dict["interpretation"]}  --weighing {param_dict["weighing"]} --timeout {param_dict["timeout"]} --disable_disjoint_mcses {param_dict["disable_disjoint_mcses"]}"""
    return PBS_script


def all_params_to_csv(fname, output_folder):
    all_params = generate_all_parameters(output_folder)
    to_csv(all_params, fname)


def COusNonIncrParamsSS(output_folder: str):
    assert output_folder.endswith('/')
    timeout = 2 * HOURS

    all_params = []
    for puzzle in puzzle_funs:
        for interpretation in [Interpretation.ACTUAL, Interpretation.FINAL, Interpretation.FULL, Interpretation.INITIAL]:
            for grow in [Grow.SAT, Grow.SUBSETMAX, Grow.MAXSAT]:
                if grow is Grow.MAXSAT:
                    for weighing in [Weighing.UNIFORM, Weighing.INVERSE, Weighing.POSITIVE]:
                        for maxsat_polarity in [True, False]:
                            params = COusNonIncrParams()

                            params.grow = grow
                            params.maxsat_polarity = maxsat_polarity
                            params.interpretation = interpretation
                            params.maxsat_weighing = weighing

                            # output
                            params.instance = puzzle
                            params.timeout = timeout
                            fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                            params.output = output_folder + puzzle + '_' + fnow + ".json"

                            # checking the setup
                            params.checkParams()
                            all_params.append(params)
                else:
                    params = COusNonIncrParams()
                    params.grow = grow
                    params.maxsat_polarity = True
                    params.interpretation = interpretation
                    params.maxsat_weighing = None
                    # output
                    params.instance = puzzle
                    params.timeout = timeout
                    # instance + date
                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    params.output = output_folder + puzzle + '_' + fnow + ".json"
                    params.checkParams()
                    all_params.append(params)
    return all_params


def COusParamsSS(output_folder: str):
    assert output_folder.endswith('/')
    timeout = 2 * HOURS

    all_params = []
    for puzzle in puzzle_funs:
        for interpretation in [Interpretation.ACTUAL, Interpretation.FINAL, Interpretation.FULL, Interpretation.INITIAL]:
            for grow in [Grow.SAT, Grow.SUBSETMAX, Grow.MAXSAT]:
                if grow is Grow.MAXSAT:
                    for weighing in [Weighing.UNIFORM, Weighing.INVERSE, Weighing.POSITIVE]:
                        for maxsat_polarity in [True, False]:
                            params = COusParams()

                            params.grow = grow
                            params.maxsat_polarity = maxsat_polarity
                            params.interpretation = interpretation
                            params.maxsat_weighing = weighing

                            # output
                            params.instance = puzzle
                            params.timeout = timeout
                            fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                            params.output = output_folder + puzzle + '_' + fnow + ".json"

                            # checking the setup
                            params.checkParams()
                            all_params.append(params)
                else:
                    params = COusParams()
                    params.grow = grow
                    params.maxsat_polarity = True
                    params.interpretation = interpretation
                    params.maxsat_weighing = None
                    # output
                    params.instance = puzzle
                    params.timeout = timeout
                    # instance + date
                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    params.output = output_folder + puzzle + '_' + fnow + ".json"
                    params.checkParams()
                    all_params.append(params)
    return all_params

def OusIncrNaiveParamsSS(output_folder: str):
    assert output_folder.endswith('/')
    all_params = []
    timeout = 2 * HOURS
    for puzzle in puzzle_funs:
        for sort_literals in [True, False]:
            for interpretation in [Interpretation.ACTUAL, Interpretation.FINAL, Interpretation.FULL, Interpretation.INITIAL]:
                for grow in [Grow.SAT, Grow.SUBSETMAX, Grow.MAXSAT]:
                    if grow is Grow.MAXSAT:
                        for weighing in [Weighing.UNIFORM, Weighing.INVERSE, Weighing.POSITIVE]:
                            for maxsat_polarity in [True, False]:
                                params = OusIncrNaiveParams()

                                params.grow = grow
                                params.maxsat_polarity = maxsat_polarity
                                params.interpretation = interpretation
                                params.maxsat_weighing = weighing

                                params.sort_literals = sort_literals

                                # output
                                params.instance = puzzle
                                params.timeout = timeout
                                fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                                params.output = output_folder + puzzle + '_' + fnow + ".json"

                                # checking the setup
                                params.checkParams()
                                all_params.append(params)
                    else:
                        params = OusIncrNaiveParams()
                        params.grow = grow
                        params.maxsat_polarity = True
                        params.interpretation = interpretation
                        params.maxsat_weighing = None
                        params.sort_literals = sort_literals
                        # output
                        params.instance = puzzle

                        # instance + date
                        params.timeout = timeout
                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"
                        params.checkParams()
                        all_params.append(params)

    return all_params

def OusIncrSharedParamsSS(output_folder: str):
    assert output_folder.endswith('/')
    all_params = []
    timeout = 2 * HOURS
    for puzzle in puzzle_funs:
        for sort_literals in [True, False]:
            for interpretation in [Interpretation.ACTUAL, Interpretation.FINAL, Interpretation.FULL, Interpretation.INITIAL]:
                for grow in [Grow.SAT, Grow.SUBSETMAX, Grow.MAXSAT]:
                    if grow is Grow.MAXSAT:
                        for weighing in [Weighing.UNIFORM, Weighing.INVERSE, Weighing.POSITIVE]:
                            for maxsat_polarity in [True, False]:
                                params = OusIncrSharedParams()

                                params.grow = grow
                                params.maxsat_polarity = maxsat_polarity
                                params.interpretation = interpretation
                                params.maxsat_weighing = weighing

                                params.sort_literals = sort_literals

                                # output
                                params.instance = puzzle
                                params.timeout = timeout
                                fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                                params.output = output_folder + puzzle + '_' + fnow + ".json"

                                # checking the setup
                                params.checkParams()
                                all_params.append(params)
                    else:
                        params = OusIncrSharedParams()
                        params.grow = grow
                        params.maxsat_polarity = True
                        params.interpretation = interpretation
                        params.maxsat_weighing = None
                        params.sort_literals = sort_literals
                        # output
                        params.instance = puzzle

                        # instance + date
                        params.timeout = timeout
                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"
                        params.checkParams()
                        all_params.append(params)


    return all_params

def OusParamsSS(output_folder: str):
    assert output_folder.endswith('/')
    all_params = []
    timeout = 2 * HOURS
    for puzzle in puzzle_funs:
        for sort_literals in [True, False]:
            for reuse_SSes in [True, False]:
                for interpretation in [Interpretation.ACTUAL, Interpretation.FINAL, Interpretation.FULL, Interpretation.INITIAL]:
                    for grow in [Grow.SAT, Grow.SUBSETMAX, Grow.MAXSAT]:
                        if grow is Grow.MAXSAT:
                            for weighing in [Weighing.UNIFORM, Weighing.INVERSE, Weighing.POSITIVE]:
                                for maxsat_polarity in [True, False]:
                                    params = OusParams()

                                    params.grow = grow
                                    params.maxsat_polarity = maxsat_polarity
                                    params.interpretation = interpretation
                                    params.maxsat_weighing = weighing

                                    params.sort_literals = sort_literals
                                    params.reuse_SSes = reuse_SSes

                                    # output
                                    params.instance = puzzle
                                    params.timeout = timeout
                                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                                    params.output = output_folder + puzzle + '_' + fnow + ".json"

                                    # checking the setup
                                    params.checkParams()
                                    all_params.append(params)
                        else:
                            params = OusParams()
                            params.grow = grow
                            params.maxsat_polarity = True
                            params.interpretation = interpretation
                            params.maxsat_weighing = None
                            params.sort_literals = sort_literals
                            params.reuse_SSes = reuse_SSes
                            # output
                            params.instance = puzzle

                            # instance + date
                            params.timeout = timeout
                            fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                            params.output = output_folder + puzzle + '_' + fnow + ".json"
                            params.checkParams()
                            all_params.append(params)
    return all_params

def MUSParamsSS(output_folder: str):
    assert output_folder.endswith('/')
    all_params = []
    timeout = 2 * HOURS

    for puzzle in puzzle_funs:
        params = MUSParams()
        # output
        params.instance = puzzle
        params.timeout = timeout
        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
        params.output = output_folder + puzzle + '_' + fnow + ".json"
        all_params.append(params)

    return all_params

if __name__ == '__main__':
    all_params_fname = "experiments/data/input/data.csv"

    output_folder = "experiments/data/output/" + datetime.now().strftime(f"%Y%m%d%H") + "/"
    input_folder = "experiments/data/input/" + datetime.now().strftime(f"%Y%m%d%H") + "/"

    all_params_to_files(input_folder=input_folder, output_folder=output_folder, params_fname=all_params_fname)

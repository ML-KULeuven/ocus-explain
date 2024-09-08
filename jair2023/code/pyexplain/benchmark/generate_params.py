#!/usr/bin/env python3

import csv
import json
from pathlib import Path
from pyexplain.examples.frietkot import *
from pyexplain.solvers.params import *
from datetime import datetime
from pyexplain.examples.utils import DEMISTIFY_FOLDER
from pyexplain.examples.utils import DEMISTIFY_MULTIPLE_SOLUTIONS_FOLDER
from pyexplain.examples.utils import DIFFICULTY_FNAME

SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAY = 24 * HOURS

TIMEOUT = 1 * HOURS

simple_puzzle_funs = {
    "simple": simpleProblem
}

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

def all_logic_puzzles(disable_easy=False):
    if disable_easy:
        return [f for f in puzzle_funs if f not in ["simple", "frietkot"]]
    return list(puzzle_funs)

def all_sudokus(n=100, only_sudoku_4x4=False, disable_sudoku_4x4=False, disable_9=False, disable_16=True, disable_25=True):
    if only_sudoku_4x4:
        return [f'sudoku-4x4_{number}.json' for number in range(9)]

    _4_4_sudokus = [f'sudoku-4x4_{number}.json' for number in range(9)]
    all_difficulties = list(difficulty for difficulty in DIFFICULTY_FNAME.keys() if difficulty != "4x4")

    if disable_16:
        all_difficulties.remove('16x16')
    if disable_25:
        all_difficulties.remove('25x25')
    if disable_9:
        all_difficulties.remove('simple')
        all_difficulties.remove('easy')
        all_difficulties.remove('intermediate')
        all_difficulties.remove('expert')
    if disable_sudoku_4x4:
        return [f'sudoku-{difficulty}_{number}.json' for difficulty in all_difficulties for number in range(n)]
    else:
        return _4_4_sudokus + [f'sudoku-{difficulty}_{number}.json' for difficulty in all_difficulties for number in range(n)]

def all_json_sudokus(n=100, only_sudoku_4x4=False, disable_sudoku_4x4=False, disable_9=False, disable_16=True, disable_25=True):
    if only_sudoku_4x4:
        return [f'sudoku-4x4-{number}' for number in range(9)]

    _4_4_sudokus = [f'sudoku-4x4-{number}' for number in range(9)]
    all_difficulties = list(difficulty for difficulty in DIFFICULTY_FNAME.keys() if difficulty != "4x4")

    if disable_16:
        all_difficulties.remove('16x16')
    if disable_25:
        all_difficulties.remove('25x25')
    if disable_9:
        all_difficulties.remove('simple')
        all_difficulties.remove('easy')
        all_difficulties.remove('intermediate')
        all_difficulties.remove('expert')
    if disable_sudoku_4x4:
        return [f'sudoku-{difficulty}_{number}.json' for difficulty in all_difficulties for number in range(n)]
    else:
        return _4_4_sudokus + [f'sudoku-{difficulty}_{number}.json' for difficulty in all_difficulties for number in range(n)]


def demystify_puzzles(n=None):
    all_puzzles = [p for p in Path(DEMISTIFY_FOLDER).iterdir() if p.is_file() and p.name.endswith('.json')]
    sorted_puzzles = [p.name for p in sorted(all_puzzles, key=lambda pi: pi.stat().st_size)]

    if n is not None:
        return sorted_puzzles[:n]

    return sorted_puzzles

def demistify_multiple_solutions(n=None):
    all_puzzles = [p for p in Path(DEMISTIFY_MULTIPLE_SOLUTIONS_FOLDER).iterdir() if p.is_file() and p.name.endswith('.json')]
    sorted_puzzles = [p.name for p in sorted(all_puzzles, key=lambda pi: pi.stat().st_size)]

    if n is not None:
        return sorted_puzzles[:n]

    return sorted_puzzles

dict_all_puzzles = {
    'all': list(puzzle_funs) + all_sudokus(25),
    'sudoku': all_sudokus(25),
    'sudoku-16-26': all_sudokus(n=25, only_sudoku_4x4=False, disable_9=True, disable_sudoku_4x4=True, disable_16=False, disable_25=False),
    'sudoku-all':all_sudokus(n=25, only_sudoku_4x4=False, disable_sudoku_4x4=False, disable_16=False, disable_25=False),
    'logic': list(puzzle_funs),
    'simple': list(simple_puzzle_funs),
    'demystify': demystify_puzzles(),
    'demystify-multiple_solutions': demistify_multiple_solutions()
}

def to_csv(params, fname):
    fieldnames = [
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
        "timeout",
        "disjoint_mcses",
        "disjoint_mcs_interpretation",
        "disjoint_mcs_weighing"
    ]

    p = Path(fname)
    with open(fname, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for param in params:
            param_dict = param.to_dict()
            for k, v in param_dict.items():
                if v is None or v == "":
                    param_dict[k] = "ignore"
            writer.writerow(param_dict)


def all_params_to_sbatch_files(all_params, base_fname, input_folder, output_folder, test_file=None):
    modulo = 1000

    if not Path(input_folder).exists():
        Path(input_folder).mkdir(parents=True)

    test_script = ["#!/bin/bash -l", ""]

    for script_id in range(len(all_params)//modulo+1):
        bash_file = Path(input_folder) / (base_fname + "run_experiments" + str(script_id)+".sh")

        script = ["#!/bin/bash -l", ""]

        for id, param in enumerate(all_params[script_id*modulo:(script_id+1)*modulo]):
            pbs_fname = base_fname + "_job_" + str(script_id*modulo+id) + ".sbatch"
            param.output = output_folder + base_fname + \
                "_results_" + str(script_id*modulo+id) + ".json"

            script.append(f"sbatch {pbs_fname}")

            test_params_joined = write_params_to_sbatch(input_folder, pbs_fname, param)

            if test_params_joined:
                test_script.append(test_params_joined)

        with bash_file.open('w+') as fp:
            fp.writelines(map(lambda x: x+"\n", script))

    if test_file is not None:
        with Path(test_file).open('w+') as fp:
            fp.writelines(map(lambda x: x+"\n", test_script))

def write_params_to_sbatch(output_folder: str, fname: str, params: BestStepParams):
    param_dict = params.to_dict()
    # print(param_dict)
    python_arguments = []

    python_arguments += ["python3 reuseSS.py"]
    for k, v in param_dict.items():
        python_arguments.append(f"--{k}")
        if v is None or v == "":
            python_arguments.append(f"ignore")
        else:
            python_arguments.append(f"{v}")

    timeout = param_dict["timeout"]
    days = timeout // (3600 * 24)
    hours = (timeout - days * 24*3600) // 3600
    sec_value = (timeout - days * 24*3600) % 3600
    min_value = sec_value // 60
    sec_value %= 60

    PBS_script = f"""#!/bin/bash

#SBATCH --job-name={fname.replace(".pbs", "")}
#SBATCH --error=%x-%j.err
#SBATCH --out=%x-%j.out
#SBATCH --ntasks=1
#SBATCH --partition=skylake,skylake_mpi
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=emilio.gamba@vub.be
#SBATCH --time={days}-{hours}:{max([30, min_value])}:{sec_value}
#SBATCH --mem=16G

module purge
module load PySAT/0.1.7.dev1-GCC-10.2.0
module load SciPy-bundle/2020.11-foss-2020b
module load Gurobi/9.1.2-GCCcore-10.2.0

pydir="/data/brussel/101/vsc10143/OCUS_EXPLAIN/code"
export PYTHONPATH=${{VSC_DATA}}/cppy_src:${{PYTHONPATH}}
export PYTHONPATH=${{VSC_DATA}}/CPMpy/:${{PYTHONPATH}}
export PYTHONPATH=${{VSC_DATA}}/cpmpy/:${{PYTHONPATH}}

cd $pydir

{" ".join(python_arguments)}
"""
    p = Path(output_folder) / fname

    with p.open('w+') as fp:
        fp.write(PBS_script)

    if "4x4" in params.instance and params.explanation_computer is ExplanationComputer.MUS:
        return " ".join(python_arguments)

    return None

def write_params_to_json(output_folder: str, fname: str, params: BestStepParams):

    file_path = Path(output_folder) / fname

    params_dict = params.to_dict()
    with file_path.open('w') as f:
        json.dump(params_dict, f)

def exec_time_greedy_corr_subsets(output_folder: str , selected_puzzles='all'):
    all_params = []
    maxsat_interpretation = Interpretation.ACTUAL
    maxsat_weighing = Weighing.UNIFORM
    maxsat_polarity = True
    # Other parameters disabled
    reuse_SSes, sort_literals = False, True

    # DISABLE Additional Improvements
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM

    timeout = TIMEOUT

    bootstrapping = {
        COusParams: [
            DisjointMCSes.DISABLED,
            DisjointMCSes.GREEDY_CORR_BOOTSTRAP_ALL,
            DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY
        ],
        OUSParallelIncrNaiveParams: [
            DisjointMCSes.DISABLED,
            DisjointMCSes.GREEDY_CORR_BOOTSTRAP_ALL,
            DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY
        ],
    }

    for puzzle in dict_all_puzzles[selected_puzzles]:
        for param_type in [
            COusParams,
            OUSParallelIncrNaiveParams
            #OusIncrNaiveParams,
        ]:
            for grow in [Grow.MAXSAT, Grow.CORR_GREEDY]:
                for disjoint_mcses in bootstrapping[param_type]:
                    ## MAXSAT Grow
                    params = param_type()
                    params.grow = grow
                    params.maxsat_polarity = maxsat_polarity

                    params.interpretation = maxsat_interpretation
                    params.maxsat_weighing = maxsat_weighing

                    params.reuse_SSes = reuse_SSes
                    params.sort_literals = sort_literals

                    params.disjoint_mcses = disjoint_mcses
                    params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                    params.disjoint_mcs_weighing = disjoint_mcs_weighing

                    params.instance = puzzle
                    params.timeout = timeout

                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    params.output = output_folder + puzzle + '_' + fnow + ".json"

                    params.checkParams()

                    all_params.append(params)

    return all_params


def exec_time_incremental_hs(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS

    for puzzle in selected_instances:
        for param_type in [
            COusNonIncrParams,
            COusNonIncrHSParams,
        ]:
            ## MAXSAT Grow
            params = param_type()
            params.load_best_params()

            params.instance = puzzle
            params.timeout = timeout

            fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
            params.output = output_folder + puzzle + '_' + fnow + ".json"

            params.checkParams()

            all_params.append(params)
    return all_params


def exec_time_sat_corr_subsets(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    param_grow = {
        COusParams:  [Grow.CORRECTION_SUBSETS_SAT],
        COusNonIncrParams:  [Grow.CORRECTION_SUBSETS_SAT],
        OUSParallelIncrNaiveParams: [Grow.CORRECTION_SUBSETS_SAT],
        OUSParallelNaiveParams: [Grow.CORRECTION_SUBSETS_SAT],
        OusIncrNaiveParams: [Grow.CORRECTION_SUBSETS_SAT],
        OusParams: [Grow.CORRECTION_SUBSETS_SAT],
    }
    grow_interpretation = {
        Grow.CORRECTION_SUBSETS_SAT: [None],
    }
    grow_weighing = {
        Grow.CORRECTION_SUBSETS_SAT: [None],
    }

    for puzzle in selected_instances:
        for param_type in [
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)
    return all_params

def exec_time_selected_grow(output_folder:str, selected_instances=None, selected_grow=Grow.CORRECTION_SUBSETS_SAT):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    assert selected_grow in list(Grow), f"Ensure select grow in {list(Grow)}"

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    param_grow = {
        COusParams:  [selected_grow],
        COusNonIncrParams:  [selected_grow],
        OUSParallelIncrNaiveParams: [selected_grow],
        OUSParallelNaiveParams: [selected_grow],
        OusIncrNaiveParams: [selected_grow],
        OusParams: [selected_grow],
    }
    grow_interpretation = {
        selected_grow: [None],
    }
    grow_weighing = {
        selected_grow: [None],
    }

    for puzzle in selected_instances:
        for param_type in [
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)
    return all_params



def exec_time_selected_grows_interpretations(output_folder:str, selected_grows, selected_interpretations, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    assert all(g in list(Grow) for g in selected_grows), f"Ensure select grow in {[g for g in selected_grows if g not in list(Grow)]}"

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    param_grow = {
        COusParams:  selected_grows,
        COusNonIncrParams:  selected_grows,
        OUSParallelIncrNaiveParams: selected_grows,
        OUSParallelNaiveParams: selected_grows,
        OusIncrNaiveParams: selected_grows,
        OusParams: selected_grows,
    }
    grow_interpretation = {
        selected_grow: selected_interpretations for selected_grow in selected_grows
    }
    grow_weighing = {
        selected_grow: [None] for selected_grow in selected_grows
    }

    for puzzle in selected_instances:
        for param_type in [
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)
    return all_params


def rq2c_paper_configs(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    param_grow = {
        MUSParams: [Grow.DISABLED],
        COusParams:  [Grow.SAT,  Grow.MAXSAT, Grow.CORR_GREEDY, Grow.DISJ_MCS],
        COusNonIncrParams:  [Grow.SAT, Grow.CORR_GREEDY],
        OUSParallelIncrNaiveParams: [Grow.SAT, Grow.MAXSAT,  Grow.CORR_GREEDY, Grow.DISJ_MCS],
        OUSParallelNaiveParams: [Grow.SAT, Grow.CORR_GREEDY],
        OusIncrNaiveParams: [Grow.SAT, Grow.MAXSAT,  Grow.CORR_GREEDY, Grow.DISJ_MCS],
        OusParams: [Grow.SAT, Grow.CORR_GREEDY],
    }
    grow_interpretation = {
        Grow.DISABLED: [None],
        Grow.SAT: [None],
        Grow.CORR_GREEDY: [Interpretation.ACTUAL],
        Grow.MAXSAT: [Interpretation.ACTUAL, Interpretation.FULL],
        Grow.DISJ_MCS: [Interpretation.ACTUAL],
    }
    grow_weighing = {
        Grow.DISABLED: [None],
        Grow.SAT: [None],
        Grow.CORR_GREEDY: [Weighing.UNIFORM],
        Grow.MAXSAT: [Weighing.UNIFORM],
        Grow.DISJ_MCS: [Weighing.UNIFORM],
    }

    for puzzle in selected_instances:
        for param_type in [
            MUSParams,
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)
    return all_params


def all_jair_params(
    output_folder,
    timeout =  1 * HOURS,
    maxsat_polarity = True,
    reuse_SSes = False,
    sort_literals = True,
    selected_instances=None):

    disjoint_mcses = DisjointMCSes.DISABLED
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM

    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    param_grow = {
        MUSParams: [
            Grow.DISABLED],
        COusParams:  [
            Grow.SAT,
            Grow.CORRECTION_SUBSETS_SAT ,
            Grow.MAXSAT,
            Grow.CORR_GREEDY,
            Grow.DISJ_MCS
            ],
        COusNonIncrParams:  [
            Grow.SAT,
            Grow.CORR_GREEDY
            ],
        OUSParallelIncrNaiveParams: [
            Grow.SAT,
            Grow.CORRECTION_SUBSETS_SAT ,
            Grow.MAXSAT,
            Grow.CORR_GREEDY,
            Grow.DISJ_MCS
            ],
        OUSParallelNaiveParams: [
            Grow.SAT,
            Grow.CORR_GREEDY
            ],
        OusIncrNaiveParams: [
            Grow.SAT,
            Grow.CORRECTION_SUBSETS_SAT ,
            Grow.MAXSAT,
            Grow.CORR_GREEDY,
            Grow.DISJ_MCS
            ],
        OusParams: [
            Grow.SAT,
            Grow.CORR_GREEDY
            ],
    }

    grow_interpretation = {
        Grow.DISABLED: [None],
        Grow.SAT: [None],
        Grow.CORRECTION_SUBSETS_SAT: [None],
        Grow.CORR_GREEDY: [Interpretation.ACTUAL],
        Grow.MAXSAT: [Interpretation.ACTUAL, Interpretation.FULL],
        Grow.DISJ_MCS: [Interpretation.ACTUAL],
    }

    grow_weighing = {
        Grow.DISABLED: [None],
        Grow.SAT: [None],
        Grow.CORRECTION_SUBSETS_SAT: [None],
        Grow.CORR_GREEDY: [Weighing.UNIFORM],
        Grow.MAXSAT: [Weighing.UNIFORM],
        Grow.DISJ_MCS: [Weighing.UNIFORM],
    }

    for param in [
            MUSParams,
            COusParams,
            OUSParallelIncrNaiveParams,
            OusIncrNaiveParams,
            COusNonIncrParams,
            OUSParallelNaiveParams,
            OusParams
        ]:
        for grow in param_grow[param]:
            for interpretation in grow_interpretation[grow]:
                for weighing in grow_weighing[grow]:
                    for puzzle in selected_instances:
                        ## MAXSAT Grow
                        params = param()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = interpretation
                        params.maxsat_weighing = weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = disjoint_mcses
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%_H%M%S%_f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)

    return all_params

def rq2_selected_config(
    output_folder:str,
    grow: Grow,
    param: BestStepParams,
    interpretation: Interpretation,
    weighing: Weighing,
    timeout =  1 * HOURS,
    selected_instances=None):

    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = timeout
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    for puzzle in selected_instances:
        ## MAXSAT Grow
        params = param()
        params.grow = grow
        params.maxsat_polarity = maxsat_polarity

        params.interpretation = interpretation
        params.maxsat_weighing = weighing

        params.reuse_SSes = reuse_SSes
        params.sort_literals = sort_literals

        params.disjoint_mcses = DisjointMCSes.DISABLED
        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
        params.disjoint_mcs_weighing = disjoint_mcs_weighing

        params.instance = puzzle
        params.timeout = timeout

        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
        params.output = output_folder + puzzle + '_' + fnow + ".json"

        params.checkParams()

        all_params.append(params)
    return all_params

def rq2_missing_configs(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    param_grow = {
        MUSParams: [Grow.DISABLED],
        COusParams:  [Grow.SAT,  Grow.MAXSAT, Grow.CORR_GREEDY, Grow.DISJ_MCS],
        COusNonIncrParams:  [Grow.SAT, Grow.CORR_GREEDY],
        OUSParallelIncrNaiveParams: [Grow.SAT, Grow.MAXSAT,  Grow.CORR_GREEDY, Grow.DISJ_MCS],
        OUSParallelNaiveParams: [Grow.SAT, Grow.CORR_GREEDY],
        OusIncrNaiveParams: [Grow.SAT, Grow.MAXSAT,  Grow.CORR_GREEDY, Grow.DISJ_MCS],
        OusParams: [Grow.SAT, Grow.CORR_GREEDY],
    }

    grow_interpretation = {
        Grow.DISABLED: [None],
        Grow.SAT: [None],
        Grow.CORR_GREEDY: [Interpretation.ACTUAL],
        Grow.MAXSAT: [Interpretation.ACTUAL, Interpretation.FULL],
        Grow.DISJ_MCS: [Interpretation.ACTUAL],
    }
    grow_weighing = {
        Grow.DISABLED: [None],
        Grow.SAT: [None],
        Grow.CORR_GREEDY: [Weighing.UNIFORM],
        Grow.MAXSAT: [Weighing.UNIFORM],
        Grow.DISJ_MCS: [Weighing.UNIFORM],
    }

    for puzzle in selected_instances:
        for param_type in [
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)
    return all_params


def rq2_maxsat_full(output_folder:str, selected_instances=None):
    ## regenerate Grow experiment: 
    # no-grow - sat - maxsat (actual - full) - on all logic puzzles+sudoku instances  
    # -> on all instances with timeout of 1hour
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True
    
    # OUSb/OUSb+Incr/OCUS/OCUS+Incr/Iterated OUS/Iterated OUS+Incr
    param_grow = {
        COusParams:  [
            Grow.MAXSAT],
        OUSParallelIncrNaiveParams: [
            Grow.MAXSAT],
        OusIncrNaiveParams: [
            Grow.MAXSAT],
    }
    grow_interpretation = {
        Grow.MAXSAT: [Interpretation.FULL],
    }
    grow_weighing = {
        Grow.MAXSAT: [Weighing.UNIFORM],
    }

    for puzzle in selected_instances:
        for param_type in [
            COusParams,
            OUSParallelIncrNaiveParams,
            OusIncrNaiveParams,
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)

    return all_params


def mus_config(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    # OUSb/OUSb+Incr/OCUS/OCUS+Incr/Iterated OUS/Iterated OUS+Incr

    for puzzle in selected_instances:

        ## MAXSAT Grow
        params = MUSParams()
        params.grow = Grow.DISABLED
        params.maxsat_polarity = maxsat_polarity

        params.interpretation = None
        params.maxsat_weighing = None

        params.reuse_SSes = reuse_SSes
        params.sort_literals = sort_literals

        params.disjoint_mcses = None
        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
        params.disjoint_mcs_weighing = disjoint_mcs_weighing

        params.instance = puzzle
        params.timeout = timeout

        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
        params.output = output_folder + puzzle + '_' + fnow + ".json"

        params.checkParams()

        all_params.append(params)

    return all_params

def RQ3b_corr_subsets(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    # OUSb/OUSb+Incr/OCUS/OCUS+Incr/Iterated OUS/Iterated OUS+Incr
    param_grow = {
        MUSParams: [Grow.DISABLED],
        COusParams:  [Grow.CORR_GREEDY],
        COusNonIncrParams:  [Grow.CORR_GREEDY],
        OUSParallelIncrNaiveParams: [Grow.CORR_GREEDY],
        OUSParallelNaiveParams: [Grow.CORR_GREEDY],
        OusIncrNaiveParams: [Grow.CORR_GREEDY],
        OusParams: [Grow.CORR_GREEDY],
    }
    grow_interpretation = {
        # Grow.DISABLED: [None],
        Grow.CORR_GREEDY: [Interpretation.ACTUAL],
    }
    grow_weighing = {
        # Grow.DISABLED: [None],
        Grow.CORR_GREEDY: [Weighing.UNIFORM],
    }

    for puzzle in selected_instances:
        for param_type in [
            # MUSParams,
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)

    return all_params

def rq3(output_folder:str, selected_instances=None):
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True

    # OUSb/OUSb+Incr/OCUS/OCUS+Incr/Iterated OUS/Iterated OUS+Incr
    param_grow = {
        MUSParams: [Grow.DISABLED],
        COusParams:  [Grow.SAT],
        COusNonIncrParams:  [Grow.SAT],
        OUSParallelIncrNaiveParams: [Grow.SAT],
        OUSParallelNaiveParams: [Grow.SAT],
        OusIncrNaiveParams: [Grow.SAT],
        OusParams: [Grow.SAT],
    }
    grow_interpretation = {
        Grow.SAT: [None],
        # Grow.CORR_GREEDY: [Interpretation.ACTUAL],
    }
    grow_weighing = {
        Grow.SAT: [None],
        # Grow.CORR_GREEDY: [Weighing.UNIFORM],
    }

    for puzzle in selected_instances:
        for param_type in [
            # MUSParams,
            COusParams,
            COusNonIncrParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
            OusParams
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)

    return all_params

def rq2(output_folder:str, selected_instances=None):
    ## regenerate Grow experiment: 
    # no-grow - sat - maxsat (actual - full) - on all logic puzzles+sudoku instances  
    # -> on all instances with timeout of 1hour
    all_params = []
    if selected_instances is None:
        selected_instances = dict_all_puzzles['all']

    timeout = 1 * HOURS
    maxsat_polarity = True
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM
    reuse_SSes = False
    sort_literals = True
    
    # OUSb/OUSb+Incr/OCUS/OCUS+Incr/Iterated OUS/Iterated OUS+Incr
    param_grow = {
        MUSParams: [
            Grow.DISABLED],
        COusParams:  [
            Grow.DISABLED, Grow.MAXSAT, Grow.SAT, Grow.CORR_GREEDY, Grow.DISJ_MCS],
        OUSParallelIncrNaiveParams: [
            Grow.DISABLED, Grow.MAXSAT, Grow.SAT, Grow.CORR_GREEDY, Grow.DISJ_MCS],
        OusIncrNaiveParams: [
            Grow.DISABLED, Grow.MAXSAT, Grow.SAT, Grow.CORR_GREEDY, Grow.DISJ_MCS],
    }
    grow_interpretation = {
        Grow.DISABLED: [None],
        Grow.MAXSAT: [Interpretation.ACTUAL, Interpretation.FULL],
        Grow.SAT: [None],
        Grow.CORR_GREEDY: [Interpretation.ACTUAL],
        Grow.DISJ_MCS: [Interpretation.ACTUAL],
    }
    grow_weighing = {
        Grow.DISABLED: [None],
        Grow.MAXSAT: [Weighing.UNIFORM],
        Grow.SAT: [None],
        Grow.CORR_GREEDY: [Weighing.UNIFORM],
        Grow.DISJ_MCS: [Weighing.UNIFORM],
    }

    for puzzle in selected_instances:
        for param_type in [
            MUSParams,
            COusParams,
            OUSParallelIncrNaiveParams,
            OusIncrNaiveParams,
        ]:
            for grow in param_grow[param_type]:
                for maxsat_interpretation in grow_interpretation[grow]:
                    for maxsat_weighing in grow_weighing[grow]:
                        ## MAXSAT Grow
                        params = param_type()
                        params.grow = grow
                        params.maxsat_polarity = maxsat_polarity

                        params.interpretation = maxsat_interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                        params.disjoint_mcs_weighing = disjoint_mcs_weighing

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)

    return all_params

def exec_time_correction_subsets(output_folder: str , selected_puzzles='all'):
    all_params = []
    maxsat_interpretation = Interpretation.ACTUAL
    maxsat_weighing = Weighing.UNIFORM
    maxsat_polarity = True
    # Other parameters disabled
    reuse_SSes, sort_literals = False, True

    # DISABLE Additional Improvements 
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM

    timeout = TIMEOUT
    bootstrapping = {
        COusNonIncrParams: [DisjointMCSes.DISABLED, DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL],
        COusParams: [DisjointMCSes.DISABLED, DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL, DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY],
        OUSParallelIncrNaiveParams: [DisjointMCSes.DISABLED, DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY, DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL],
        OUSParallelNaiveParams: [DisjointMCSes.DISABLED, DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY],
        OusIncrNaiveParams: [DisjointMCSes.DISABLED, DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL, DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY],
    }

    for puzzle in dict_all_puzzles[selected_puzzles]:
        for param_type in [
            COusNonIncrParams,
            COusParams,
            OUSParallelIncrNaiveParams,
            OUSParallelNaiveParams,
            OusIncrNaiveParams,
        ]:
            for grow in [Grow.MAXSAT, Grow.DISJ_MCS]:
                for disjoint_mcses in bootstrapping[param_type]:
                    ## MAXSAT Grow
                    params = param_type()
                    params.grow = grow
                    params.maxsat_polarity = maxsat_polarity

                    params.interpretation = maxsat_interpretation
                    params.maxsat_weighing = maxsat_weighing

                    params.reuse_SSes = reuse_SSes
                    params.sort_literals = sort_literals

                    params.disjoint_mcses = disjoint_mcses
                    params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                    params.disjoint_mcs_weighing = disjoint_mcs_weighing

                    params.instance = puzzle
                    params.timeout = timeout

                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    params.output = output_folder + puzzle + '_' + fnow + ".json"

                    params.checkParams()

                    all_params.append(params)

    return all_params

def all_grow_configs(output_folder: str , selected_puzzles='all'):
    timeout = TIMEOUT
    all_params = []
    reuse_SSes, sort_literals = False, True
    grow_interpretation = {
        Grow.DISABLED:  [Interpretation.FULL],
        Grow.SUBSETMAX: [Interpretation.ACTUAL, Interpretation.FULL],
        Grow.SAT:       [Interpretation.FULL],
        Grow.MAXSAT:    [Interpretation.ACTUAL, Interpretation.FULL]
    }
    grow_weighing = {
        Grow.DISABLED:  [Weighing.UNIFORM],
        Grow.SUBSETMAX: [Weighing.UNIFORM],
        Grow.SAT:       [Weighing.UNIFORM],
        Grow.MAXSAT:    [Weighing.POSITIVE,Weighing.INVERSE, Weighing.UNIFORM]
    }
    grow_polarity = {
        Grow.DISABLED: [False],
        Grow.SUBSETMAX: [True, False],
        Grow.SAT: [True, False],
        Grow.MAXSAT: [True, False]
    }

    for puzzle in dict_all_puzzles[selected_puzzles]:
        for grow in [
            Grow.DISABLED, Grow.SUBSETMAX, Grow.SAT, Grow.MAXSAT
        ]:
            for maxsat_weighing in grow_weighing[grow]:
                for interpretation in grow_interpretation[grow]:
                    for polarity in grow_polarity[grow]:
                        ## MAXSAT Grow
                        params = COusNonIncrParams()
                        params.grow = grow
                        params.maxsat_polarity = polarity

                        params.interpretation = interpretation
                        params.maxsat_weighing = maxsat_weighing

                        params.reuse_SSes = reuse_SSes
                        params.sort_literals = sort_literals

                        params.disjoint_mcses = DisjointMCSes.DISABLED
                        params.disjoint_mcs_interpretation = Interpretation.ACTUAL
                        params.disjoint_mcs_weighing =  Weighing.UNIFORM

                        params.instance = puzzle
                        params.timeout = timeout

                        fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        params.output = output_folder + puzzle + '_' + fnow + ".json"

                        params.checkParams()

                        all_params.append(params)

    return all_params

def exect_ime_given_instances(output_folder: str, selected_instances: list):
    """The best configurations are

    For Iterated Incremental OUS:
        - Greedy correction subsets + Greedy Corr. pre-processing only or disabled)
    For Incremental OCUS:
        - Disj. MCS/MaxSAT +  Bootstrap All with Disj.MCS

    Args:
        output_folder (str): Output folder on HPC
        selected_instances ([str]): List of isntance names

    Returns:
        [bestStepparams]: List of parameters
    """

    all_params = []
    maxsat_interpretation = Interpretation.ACTUAL
    maxsat_weighing = Weighing.UNIFORM
    maxsat_polarity = True

    # Other parameters disabled
    reuse_SSes, sort_literals = False, True

    # DISABLE Additional Improvements
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM

    timeout = 1 * HOURS + 0 * MINUTES + 00 * SECONDS

    all_bootstrapping = {
        OUSParallelIncrNaiveParams: [
            DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY, 
            DisjointMCSes.DISABLED
        ],
        COusParams:[
            DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL
        ]
    }
    all_grow = {
        OUSParallelIncrNaiveParams: [
            Grow.CORR_GREEDY
        ],
        COusParams:[
            Grow.DISJ_MCS,
            Grow.MAXSAT,
            # Grow.CORR_GREEDY
        ]
    }

    for param_type in [OUSParallelIncrNaiveParams, COusParams]:
        for instance in selected_instances:
            for disjoint_mcses in all_bootstrapping[param_type]:
                for grow in all_grow[param_type]:
                    ## MAXSAT Grow
                    params = param_type()
                    params.grow = grow
                    params.maxsat_polarity = maxsat_polarity

                    params.interpretation = maxsat_interpretation
                    params.maxsat_weighing = maxsat_weighing

                    params.reuse_SSes = reuse_SSes
                    params.sort_literals = sort_literals

                    params.disjoint_mcses = disjoint_mcses
                    params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                    params.disjoint_mcs_weighing = disjoint_mcs_weighing

                    params.instance = instance
                    params.timeout = timeout

                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    params.output = output_folder + instance.replace(".json", '') + '_' + fnow + ".json"

                    params.checkParams()

                    all_params.append(params)

    return all_params

def exec_time_best_config(output_folder: str , selected_puzzles='all', n=None):
    all_params = []
    maxsat_interpretation = Interpretation.ACTUAL
    maxsat_weighing = Weighing.UNIFORM
    maxsat_polarity = True
    # Other parameters disabled
    reuse_SSes, sort_literals = False, True

    # DISABLE Additional Improvements
    disjoint_mcs_interpretation = Interpretation.ACTUAL
    disjoint_mcs_weighing = Weighing.UNIFORM

    timeout = TIMEOUT

    bootstrapping = {
        OUSParallelIncrNaiveParams: [
            DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY
        ]
    }
    all_puzzles = dict_all_puzzles[selected_puzzles]

    if n:
        all_puzzles = all_puzzles[:n]

    for puzzle in all_puzzles:
        for param_type in [
            OUSParallelIncrNaiveParams
        ]:
            for grow in [Grow.CORR_GREEDY]:
                for disjoint_mcses in bootstrapping[param_type]:
                    ## MAXSAT Grow
                    params = param_type()
                    params.grow = grow
                    params.maxsat_polarity = maxsat_polarity

                    params.interpretation = maxsat_interpretation
                    params.maxsat_weighing = maxsat_weighing

                    params.reuse_SSes = reuse_SSes
                    params.sort_literals = sort_literals

                    params.disjoint_mcses = disjoint_mcses
                    params.disjoint_mcs_interpretation = disjoint_mcs_interpretation
                    params.disjoint_mcs_weighing = disjoint_mcs_weighing

                    params.instance = puzzle
                    params.timeout = timeout

                    fnow = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    params.output = output_folder + puzzle + '_' + fnow + ".json"

                    params.checkParams()

                    all_params.append(params)

    return all_params
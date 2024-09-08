## regenerate Grow experiment: no-grow - sat - maxsat (actual - full) - on all logic puzzles+sudoku instances  -> on all instances with timeout of 1hour
## regenerate MUS + [OUSb/OUSb+Incr/OCUS/OCUS+Incr/Iterated OUS/Iterated OUS+Incr] x MaxSAT best - on all logic puzzles+sudoku  -> on all instances with timeout of 1hour
## regenerate MUS + [OUSb+Incr/OCUS+Incr/Iterated OUS+Incr] x [Corr Subsets/Greedy Corr Subsets] - on all logic puzzles+sudoku  -> on all instances with timeout of 1hour


# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
import json
from generate_params import all_logic_puzzles, all_params_to_sbatch_files, demystify_puzzles, exect_ime_given_instances, puzzle_funs, all_sudokus, rq2, rq2_maxsat_full

environment = 'LINUX'
BASE_MAC_LINUX = {
    'MAC': '/Users/emiliogamba/Documents/GitHub/',
    'LINUX': '/home/emilio/research/'
}

PYEXPLAIN_LOCAL_FOLDER = BASE_MAC_LINUX[environment] +"OCUSExplanations/code/"
LOCAL_BASE_EXPERIMENTS = BASE_MAC_LINUX[environment] +"hpc_experiments2/experiments/data/"

HPC_BASE_EXPERIMENTS = "/data/brussel/101/vsc10143/hpc_experiments2/experiments/data/"

LOCAL_INPUT     = LOCAL_BASE_EXPERIMENTS + "input/"
LOCAL_OUTPUT    = LOCAL_BASE_EXPERIMENTS + "output/"

HPC_INPUT       = HPC_BASE_EXPERIMENTS + "input/"
HPC_OUTPUT      = HPC_BASE_EXPERIMENTS + "output/"

CURRENT_HOUR = datetime.now().strftime(f"%Y%m%d%H") + "/"

### EPXERIMENT RQ2

RQ2_LOGIC_SUDOKU_PUZZLES = "RQ2_LOGIC_SUDOKU_PUZZLES_MAXSAT_FULL/" + CURRENT_HOUR

RQ2_LOGIC_SUDOKU_PUZZLES_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + RQ2_LOGIC_SUDOKU_PUZZLES
RQ2_LOGIC_SUDOKU_PUZZLES_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
RQ2_LOGIC_SUDOKU_PUZZLES_HPC_OUTPUT_FOLDER = HPC_OUTPUT + RQ2_LOGIC_SUDOKU_PUZZLES

RQ2_LOGIC_SUDOKU_PUZZLES_LOCAL_INPUT_FOLDER = LOCAL_INPUT + RQ2_LOGIC_SUDOKU_PUZZLES
RQ2_LOGIC_SUDOKU_PUZZLES_HPC_INPUT_FOLDER = HPC_INPUT + RQ2_LOGIC_SUDOKU_PUZZLES

RQ2_DEMYSTIFY_PUZZLES = "RQ2_DEMYSTIFY_PUZZLES_MAXSAT_FULL/" + CURRENT_HOUR

RQ2_DEMYSTIFY_PUZZLES_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + RQ2_DEMYSTIFY_PUZZLES
RQ2_DEMYSTIFY_PUZZLES_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
RQ2_DEMYSTIFY_PUZZLES_HPC_OUTPUT_FOLDER = HPC_OUTPUT + RQ2_DEMYSTIFY_PUZZLES

RQ2_DEMYSTIFY_PUZZLES_LOCAL_INPUT_FOLDER = LOCAL_INPUT + RQ2_DEMYSTIFY_PUZZLES
RQ2_DEMYSTIFY_PUZZLES_HPC_INPUT_FOLDER = HPC_INPUT + RQ2_DEMYSTIFY_PUZZLES


def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")

base_fname_RQ2_LOGIC_SUDOKU_PUZZLES = "RQ2_LOGIC_SUDOKU_PUZZLES_"
base_fname_RQ2_DEMYSTIFY_PUZZLES = "RQ2_DEMYSTIFY_PUZZLES_"

# START WITH LOGIC PUZZLES and SUDOKU
logic_sudoku_instances = all_logic_puzzles(disable_easy=True) + all_sudokus(n=25, disable_sudoku_4x4=True)

print(all_sudokus(n=25, disable_sudoku_4x4=True))
# REMAINING INSTANCES
difficult_demystify_instances= ['miracle_miracle_0_original.param.json', 'skyscrapers_skyscrapers_16_2-high-numbers.param.json', 'x-sums_x-sums_0_ctc-best-xsums.param.json']
demystify_instances = [puzzle for puzzle in demystify_puzzles() if "sudoku" not in puzzle and puzzle not in difficult_demystify_instances]

all_params_RQ2_LOGIC_SUDOKU_PUZZLES = rq2_maxsat_full(
    output_folder=RQ2_LOGIC_SUDOKU_PUZZLES_HPC_OUTPUT_FOLDER,
    selected_instances=logic_sudoku_instances
)

all_params_RQ2_DEMYSTIFY_PUZZLES = rq2_maxsat_full(
    output_folder=RQ2_DEMYSTIFY_PUZZLES_HPC_OUTPUT_FOLDER,
    selected_instances=demystify_instances
)

print(f"{len(all_params_RQ2_LOGIC_SUDOKU_PUZZLES)=}")
print(f"{len(all_params_RQ2_DEMYSTIFY_PUZZLES)=}")

all_params_to_sbatch_files(
    all_params=all_params_RQ2_LOGIC_SUDOKU_PUZZLES,
    base_fname=base_fname_RQ2_LOGIC_SUDOKU_PUZZLES,
    input_folder=RQ2_LOGIC_SUDOKU_PUZZLES_LOCAL_INPUT_FOLDER,
    output_folder=RQ2_LOGIC_SUDOKU_PUZZLES_HPC_OUTPUT_FOLDER
)

ini_folder(RQ2_LOGIC_SUDOKU_PUZZLES_LOCAL_OUTPUT_FOLDER)

all_params_to_sbatch_files(
    all_params=all_params_RQ2_DEMYSTIFY_PUZZLES,
    base_fname=base_fname_RQ2_DEMYSTIFY_PUZZLES,
    input_folder=RQ2_DEMYSTIFY_PUZZLES_LOCAL_INPUT_FOLDER,
    output_folder=RQ2_DEMYSTIFY_PUZZLES_HPC_OUTPUT_FOLDER
)

ini_folder(RQ2_DEMYSTIFY_PUZZLES_LOCAL_OUTPUT_FOLDER)

## RQ3: 

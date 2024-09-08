# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
import json
from generate_params import RQ3b_corr_subsets, all_jair_params, all_logic_puzzles, all_params_to_sbatch_files, demystify_puzzles, exect_ime_given_instances, puzzle_funs, all_sudokus, rq2, rq2c_paper_configs, rq3

def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")

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
ALL_PUZZLES = "PUZZLES/" + CURRENT_HOUR

ALL_PUZZLES_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + ALL_PUZZLES
ALL_PUZZLES_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
ALL_PUZZLES_HPC_OUTPUT_FOLDER = HPC_OUTPUT + ALL_PUZZLES

ALL_PUZZLES_LOCAL_INPUT_FOLDER = LOCAL_INPUT + ALL_PUZZLES
ALL_PUZZLES_HPC_INPUT_FOLDER = HPC_INPUT + ALL_PUZZLES

base_fname_ALL_PUZZLES = "ALL_PUZZLES_"

# REMAINING INSTANCES
all_instances = all_sudokus(n=25, disable_sudoku_4x4=True) + all_logic_puzzles(disable_easy=True) + demystify_puzzles()

all_params_ALL_PUZZLES = all_jair_params(
    output_folder=ALL_PUZZLES_HPC_OUTPUT_FOLDER,
    selected_instances=all_instances
)

all_params_to_sbatch_files(
    all_params=all_params_ALL_PUZZLES,
    base_fname=base_fname_ALL_PUZZLES,
    input_folder=ALL_PUZZLES_LOCAL_INPUT_FOLDER,
    output_folder=ALL_PUZZLES_HPC_OUTPUT_FOLDER
)

ini_folder(ALL_PUZZLES_LOCAL_OUTPUT_FOLDER)

print(f"{len(all_params_ALL_PUZZLES)=}")


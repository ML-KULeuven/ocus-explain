
# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
import json

from generate_params import all_json_sudokus, all_params_to_sbatch_files, exec_time_best_config, exec_time_greedy_corr_subsets, exect_ime_given_instances, all_sudokus

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

SUDOKU_DIFFICULT = "SUDOKU_DIFFICULT/" + CURRENT_HOUR

SUDOKU_DIFFICULT_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + SUDOKU_DIFFICULT
SUDOKU_DIFFICULT_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
SUDOKU_DIFFICULT_HPC_OUTPUT_FOLDER = HPC_OUTPUT + SUDOKU_DIFFICULT

SUDOKU_DIFFICULT_LOCAL_INPUT_FOLDER = LOCAL_INPUT + SUDOKU_DIFFICULT
SUDOKU_DIFFICULT_HPC_INPUT_FOLDER = HPC_INPUT + SUDOKU_DIFFICULT

def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")

base_fname_all_configs = "greedy_SUDOKU_DIFFICULT_"

difficult_sudoku_instances = all_json_sudokus(
    n=100,
    only_sudoku_4x4=False, disable_sudoku_4x4=True, disable_9=True, disable_16=False, disable_25=False
)

print(difficult_sudoku_instances)

all_params = exect_ime_given_instances(
    output_folder=SUDOKU_DIFFICULT_HPC_OUTPUT_FOLDER, 
    selected_instances=difficult_sudoku_instances
)

all_params_to_sbatch_files(
    all_params=all_params,
    base_fname=base_fname_all_configs,
    input_folder=SUDOKU_DIFFICULT_LOCAL_INPUT_FOLDER,
    output_folder=SUDOKU_DIFFICULT_HPC_OUTPUT_FOLDER
)

ini_folder(SUDOKU_DIFFICULT_LOCAL_OUTPUT_FOLDER)
print(len(all_params))

# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
from pyexplain.solvers.params import Grow
from generate_params import all_logic_puzzles, all_params_to_sbatch_files, demystify_puzzles, all_sudokus, exec_time_selected_grow


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

SAT_CORR_SUBSETS = "RQ2_SAT_CORR_SUBSETS/" + CURRENT_HOUR

SAT_CORR_SUBSETS_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + SAT_CORR_SUBSETS
SAT_CORR_SUBSETS_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
SAT_CORR_SUBSETS_HPC_OUTPUT_FOLDER = HPC_OUTPUT + SAT_CORR_SUBSETS

SAT_CORR_SUBSETS_LOCAL_INPUT_FOLDER = LOCAL_INPUT + SAT_CORR_SUBSETS
SAT_CORR_SUBSETS_HPC_INPUT_FOLDER = HPC_INPUT + SAT_CORR_SUBSETS

base_fname_all_configs = "subsetmax_correction_subsets_"

# REMAINING INSTANCES
all_instances = all_sudokus(n=25, disable_sudoku_4x4=True) + all_logic_puzzles(disable_easy=True) + demystify_puzzles()

all_params = exec_time_selected_grow(
    output_folder=SAT_CORR_SUBSETS_HPC_OUTPUT_FOLDER, 
    selected_instances=all_instances,
    selected_grow=Grow.SUBSETMAX
)

all_params_to_sbatch_files(
    all_params=all_params,
    base_fname=base_fname_all_configs,
    input_folder=SAT_CORR_SUBSETS_LOCAL_INPUT_FOLDER,
    output_folder=SAT_CORR_SUBSETS_HPC_OUTPUT_FOLDER
)

ini_folder(SAT_CORR_SUBSETS_LOCAL_OUTPUT_FOLDER)
print(len(all_params))
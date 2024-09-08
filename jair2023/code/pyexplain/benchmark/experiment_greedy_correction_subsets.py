
# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
from generate_params import all_params_to_sbatch_files, exec_time_greedy_corr_subsets

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

CORRECTION_SUBSETS = "CORRECTION_SUBSETS/" + CURRENT_HOUR

CORRECTION_SUBSETS_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + CORRECTION_SUBSETS
CORRECTION_SUBSETS_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
CORRECTION_SUBSETS_HPC_OUTPUT_FOLDER = HPC_OUTPUT + CORRECTION_SUBSETS

CORRECTION_SUBSETS_LOCAL_INPUT_FOLDER = LOCAL_INPUT + CORRECTION_SUBSETS
CORRECTION_SUBSETS_HPC_INPUT_FOLDER = HPC_INPUT + CORRECTION_SUBSETS

base_fname_all_configs = "greedy_correction_subsets_"

all_params = exec_time_greedy_corr_subsets(
    output_folder=CORRECTION_SUBSETS_HPC_OUTPUT_FOLDER, 
    selected_puzzles='all'
)

all_params_to_sbatch_files(
    all_params=all_params,
    base_fname=base_fname_all_configs,
    input_folder=CORRECTION_SUBSETS_LOCAL_INPUT_FOLDER,
    output_folder=CORRECTION_SUBSETS_HPC_OUTPUT_FOLDER
)

ini_folder(CORRECTION_SUBSETS_LOCAL_OUTPUT_FOLDER)
print(len(all_params))
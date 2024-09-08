
# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
from generate_params import all_params_to_files, all_params_to_sbatch_files, exec_time_grow_sat_mip_all_configs
# from pyexplain.benchmark.generate_params import all_params_to_files, best_grow_difficult_sudoku_configs, best_grow_mus_configs, best_grow_ous_configs

def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")
# Comparison of time to compute:
# 1. Optimal Hitting Set
# 2. Grows
# 3. SAT call
# PYEXPLAIN_LOCAL_FOLDER = "/home/emilio/research/OCUSExplain/code/"
# LOCAL_BASE_EXPERIMENTS = "/home/emilio/research/hpc_experiments2/experiments/data/"

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

GROW_SAT_MIP = "GROW_SAT_MIP/" + CURRENT_HOUR

GROW_SAT_MIP_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + GROW_SAT_MIP
GROW_SAT_MIP_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
GROW_SAT_MIP_HPC_OUTPUT_FOLDER = HPC_OUTPUT + GROW_SAT_MIP

GROW_SAT_MIP_LOCAL_INPUT_FOLDER = LOCAL_INPUT + GROW_SAT_MIP
GROW_SAT_MIP_HPC_INPUT_FOLDER = HPC_INPUT + GROW_SAT_MIP


base_fname_all_configs = "all_configs_"

all_params = exec_time_grow_sat_mip_all_configs(
    output_folder=GROW_SAT_MIP_HPC_OUTPUT_FOLDER
)

all_params_to_sbatch_files(
    all_params=all_params,
    base_fname=base_fname_all_configs,
    input_folder=GROW_SAT_MIP_LOCAL_INPUT_FOLDER,
    output_folder=GROW_SAT_MIP_HPC_OUTPUT_FOLDER
)

ini_folder(GROW_SAT_MIP_LOCAL_OUTPUT_FOLDER)

# all_simple_params = exec_time_grow_sat_mip_all_configs(
#     output_folder=GROW_SAT_MIP_LOCAL_TEST_OUTPUT_FOLDER, selected_puzzles='simple'
# )

# from importlib.machinery import SourceFileLoader
  
# # imports the module from the given path
# foo = SourceFileLoader("reuseSS","/Users/emiliogamba/Documents/GitHub/OCUSExplanations/code/reuseSS.py").load_module()

# for simple_param in all_simple_params:
#     foo.runpuzzle(simple_param)
# which configurations to test?
# From notebooks/2021_jair_experiments.ipynb
# -> OCUS Incr.
# -> Ocus Non-Incr
# -> OUSb iterative Incr.
# -> OUSb iterative Non-incr.
# -> OUSb Lit Incr. HS

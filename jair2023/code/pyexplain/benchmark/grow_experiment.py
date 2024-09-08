from datetime import datetime
from pathlib import Path
from pyexplain.benchmark.generate_params import all_grow_configs, all_params_to_sbatch_files


def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")


PYEXPLAIN_LOCAL_FOLDER = "/Users/emiliogamba/Documents/GitHub/OCUSExplanations/code/"
LOCAL_BASE_EXPERIMENTS = "/Users/emiliogamba/Documents/GitHub/hpc_experiments2/experiments/data/"

HPC_BASE_EXPERIMENTS = "/data/brussel/101/vsc10143/hpc_experiments2/experiments/data/"

LOCAL_OUTPUT = LOCAL_BASE_EXPERIMENTS + "output/"
HPC_OUTPUT = HPC_BASE_EXPERIMENTS + "output/"

LOCAL_INPUT = LOCAL_BASE_EXPERIMENTS + "input/"
HPC_INPUT = HPC_BASE_EXPERIMENTS + "input/"

GROW = "GROW/"
SUDOKU = "SUDOKU/"

CURRENT_HOUR = datetime.now().strftime(f"%Y%m%d%H") + "/"

# output/input folders
output_folder = HPC_OUTPUT + CURRENT_HOUR
local_output_folder = LOCAL_OUTPUT + CURRENT_HOUR
input_folder = LOCAL_INPUT + CURRENT_HOUR

# GROW INPUT-OUPUT
logic_grow_output_folder = HPC_OUTPUT + GROW + CURRENT_HOUR
sudoku_grow_output_folder = HPC_OUTPUT + GROW + CURRENT_HOUR

all_grow_local_output_folder = LOCAL_OUTPUT + GROW  + CURRENT_HOUR

sudoku_grow_input_folder = LOCAL_INPUT + GROW + SUDOKU + CURRENT_HOUR

### GROW
base_fname_grow_sudoku = "difficult_grow_sudoku_"

all_grow_params = all_grow_configs(sudoku_grow_output_folder)

print(len(all_grow_params))
all_params_to_sbatch_files(
    all_params=all_grow_params,
    base_fname=base_fname_grow_sudoku,
    input_folder=sudoku_grow_input_folder,
    output_folder=sudoku_grow_output_folder
)

ini_folder(all_grow_local_output_folder)

# generate experiemnts for grow with explanation sequences
# generate experiemnts for grow with unsatisfiable instances
# generate experiments for

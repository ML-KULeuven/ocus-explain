from datetime import datetime
from pathlib import Path
from generate_params import all_params_to_files, all_puzzles_config_params, all_puzzles_grow_params, best_grow_all_configs


def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")


PYEXPLAIN_LOCAL_FOLDER = "/home/emilio/research/OCUSExplain/code/"

LOCAL_BASE_EXPERIMENTS = "/home/emilio/research/hpc_experiments2/experiments/data/"
HPC_BASE_EXPERIMENTS = "/data/brussel/101/vsc10143/hpc_experiments2/experiments/data/"

LOCAL_OUTPUT = LOCAL_BASE_EXPERIMENTS + "output/"
HPC_OUTPUT = HPC_BASE_EXPERIMENTS + "output/"

LOCAL_INPUT = LOCAL_BASE_EXPERIMENTS + "input/"
HPC_INPUT = HPC_BASE_EXPERIMENTS + "input/"

GROW = "GROW/"
CONFIG = "CONFIG/"
LOGIC = "LOGIC/"
SUDOKU = "SUDOKU/"

CURRENT_HOUR = datetime.now().strftime(f"%Y%m%d%H") + "/"

# output/input folders
output_folder = HPC_OUTPUT + CURRENT_HOUR
local_output_folder = LOCAL_OUTPUT + CURRENT_HOUR
input_folder = LOCAL_INPUT + CURRENT_HOUR

# GROW INPUT-OUPUT
logic_grow_output_folder = HPC_OUTPUT + GROW + LOGIC+ CURRENT_HOUR
sudoku_grow_output_folder = HPC_OUTPUT + GROW + SUDOKU + CURRENT_HOUR

logic_grow_local_output_folder = LOCAL_OUTPUT + GROW  + LOGIC + CURRENT_HOUR
sudoku_grow_local_output_folder = LOCAL_OUTPUT + GROW + SUDOKU + CURRENT_HOUR

logic_grow_input_folder = LOCAL_INPUT + GROW + LOGIC +  CURRENT_HOUR
sudoku_grow_input_folder = LOCAL_INPUT + GROW + SUDOKU + CURRENT_HOUR

### GROW
all_logic_grow_params = all_puzzles_grow_params(logic_grow_output_folder, 'logic')
all_sudoku_grow_params = all_puzzles_grow_params(sudoku_grow_output_folder, 'sudoku')

print("all_logic_grow_params=", len(all_logic_grow_params))
print("all_sudoku_grow_params=", len(all_sudoku_grow_params))
base_fname_grow = "grow_"


# CONFIGS INPUT/OUTPUT
logic_config_output_folder = HPC_OUTPUT + CONFIG + LOGIC  + CURRENT_HOUR
sudoku_config_output_folder = HPC_OUTPUT + CONFIG + SUDOKU + CURRENT_HOUR

logic_config_local_output_folder = LOCAL_OUTPUT + CONFIG + LOGIC + CURRENT_HOUR
sudoku_config_local_output_folder = LOCAL_OUTPUT + CONFIG + SUDOKU + CURRENT_HOUR

logic_config_input_folder = LOCAL_INPUT + CONFIG  + LOGIC + CURRENT_HOUR
sudoku_config_input_folder = LOCAL_INPUT + CONFIG + SUDOKU + CURRENT_HOUR

### CONFIGS
all_logic_config_params = all_puzzles_config_params(logic_config_output_folder, 'logic')
all_sudoku_config_params = all_puzzles_config_params(sudoku_config_output_folder, 'sudoku')

print("all_logic_config_params=", len(all_logic_config_params))
print("all_sudoku_config_params=", len(all_sudoku_config_params))

base_fname_config_logic = "config_logic_"
base_fname_config_sudoku = "config_sudoku_"
base_fname_grow_logic = "grow_logic_"
base_fname_grow_sudoku = "grow_sudoku_"

all_params_to_files(all_logic_grow_params, base_fname=base_fname_grow_logic, input_folder=logic_grow_input_folder,
                    output_folder=logic_grow_output_folder, test_file=PYEXPLAIN_LOCAL_FOLDER + "test_logic_grow.sh")
ini_folder(logic_grow_local_output_folder)

all_params_to_files(all_logic_config_params, base_fname=base_fname_config_logic, input_folder=logic_config_input_folder,
                    output_folder=logic_config_output_folder, test_file=PYEXPLAIN_LOCAL_FOLDER + "test_logic_config.sh")
ini_folder(logic_config_local_output_folder)

all_params_to_files(all_sudoku_grow_params, base_fname=base_fname_grow_sudoku, input_folder=sudoku_grow_input_folder,
                    output_folder=sudoku_grow_output_folder, test_file=PYEXPLAIN_LOCAL_FOLDER + "test_sudoku_grow.sh")
ini_folder(sudoku_grow_local_output_folder)

all_params_to_files(all_sudoku_config_params, base_fname=base_fname_config_sudoku, input_folder=sudoku_config_input_folder,
                    output_folder=sudoku_config_output_folder, test_file=PYEXPLAIN_LOCAL_FOLDER + "test_sudoku_config.sh")
ini_folder(sudoku_config_local_output_folder)

# generate experiemnts for grow with explanation sequences

all_logic_grow_params = best_grow_all_configs(logic_grow_output_folder, 'logic')
all_sudoku_grow_params = best_grow_all_configs(sudoku_grow_output_folder, 'sudoku')

print("all_logic_grow_params=", len(all_logic_grow_params))
print("all_sudoku_grow_params=", len(all_sudoku_grow_params))

# base_fname_grow = "best_grow_"

base_fname_grow_logic = "best_grow_logic_"
base_fname_grow_sudoku = "best_grow_sudoku_"

all_params_to_files(all_logic_grow_params, base_fname=base_fname_grow_logic, input_folder=logic_grow_input_folder,
                    output_folder=logic_grow_output_folder, test_file=PYEXPLAIN_LOCAL_FOLDER + "test_logic_grow.sh")

ini_folder(logic_grow_local_output_folder)

all_params_to_files(all_sudoku_grow_params, base_fname=base_fname_grow_sudoku, input_folder=sudoku_grow_input_folder,
                    output_folder=sudoku_grow_output_folder, test_file=PYEXPLAIN_LOCAL_FOLDER + "test_sudoku_grow.sh")

ini_folder(sudoku_grow_local_output_folder)

# generate experiemnts for grow with unsatisfiable instances

# generate experiments for

from datetime import datetime
from generate_params import all_params_to_files,all_params_to_csv

simple_fname = "experiments/data/input/data_simple.csv"
all_params_fname = "experiments/data/input/data.csv"
output_folder = "experiments/data/output/" + datetime.now().strftime(f"%Y%m%d%H") + "/"
input_folder = "experiments/data/input/" + datetime.now().strftime(f"%Y%m%d%H") + "/"
base_fname = "reuseSS_" + datetime.now().strftime(f"%Y%m%d")

all_params_to_files(input_folder=input_folder, output_folder=output_folder)

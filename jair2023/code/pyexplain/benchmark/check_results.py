from pathlib import Path
import re
import json

# MAC
environment = 'LINUX'
BASE_MAC_LINUX = {
    'MAC': '/Users/emiliogamba/Documents/GitHub/',
    'LINUX': '/home/emilio/research/'
}

PATH_FIGURES_POST_PAPER = Path(BASE_MAC_LINUX[environment] + "holygrail/latex/journal/jair21/figures/")
EXPERIMENT_RESULTS = Path(BASE_MAC_LINUX[environment] + "hpc_experiments2/experiments/data/output/")
BASE_OUTPUT_PATH = BASE_MAC_LINUX[environment] + "/hpc_experiments2/experiments/data/output/"
BASE_INPUT_PATH = BASE_MAC_LINUX[environment] + "/hpc_experiments2/experiments/data/input/"

BASE_LOCAL = "/Users/emiliogamba/Documents/GitHub/hpc_experiments2/experiments/data/"

INPUT_FOLDER = BASE_LOCAL + "input/CORRECTION_SUBSETS/2021120315/"
OUTPUT_FOLDER =  BASE_LOCAL + "output/CORRECTION_SUBSETS/2021120315/"

SUDOKU_BASE_INPUT_NAME = "sudoku_corr_subsset__job_"
LOGIC_BASE_INPUT_NAME = "logic_corr_subsset__job_"

SUDOKU_BASE_OUTPUT_NAME = "sudoku_corr_subsset__results_"
LOGIC_BASE_OUTPUT_NAME = "logic_corr_subsset__results_"

def check_wrongly_timedout(df):
    wrongly_timedout = []
    for expl_config in set(df["explanation config"]):
        df_expl_config = df[
            (df["explanation config"]== expl_config) &
            (df["time_timedout"])
        ]
        for _, row in df_expl_config.iterrows():
            ## check if there exists another puzzle with same number of lits derived 
            instance = row["params_instance"]
            non_timedout_instance = df[
                (~df["time_timedout"])&
                (df["params_instance"] == instance)
            ]
            tot_lits_derived = row["tot_lits_derived"]

            if len(non_timedout_instance) > 0:
                isntances_tot_lits_derived = set(non_timedout_instance["tot_lits_derived"])
                if len(isntances_tot_lits_derived) != 1:
                    print(instance, isntances_tot_lits_derived)
                # assert len(isntances_tot_lits_derived) == 1, "Only 1 number of lits derived"
                if next(iter(isntances_tot_lits_derived)) == tot_lits_derived:
                    wrongly_timedout.append((row["params_output"], next(iter(isntances_tot_lits_derived)),tot_lits_derived))

    return wrongly_timedout

def check_wrongly_not_timedout(df):
    wrongly_non_timedout_instances = []
    wrongly_non_timedout = []

    for expl_config in set(df["explanation config"]):
        df_expl_config = df[
            (df["explanation config"]== expl_config) &
            (~df["time_timedout"])
        ]
        for _, row in df_expl_config.iterrows():
            ## check if there exists another puzzle with same number of lits derived 
            instance = row["params_instance"]
            non_timedout_instance_lits_derived = set(df[
                (~df["time_timedout"]) &
                (df["params_instance"] == instance)
            ]["tot_lits_derived"])

            if len(non_timedout_instance_lits_derived) > 1:
                wrongly_non_timedout_instances.append(row["params_instance"])

            assert len(non_timedout_instance_lits_derived) <= 1, "More than 1 # of derived instances"
            assert next(iter(non_timedout_instance_lits_derived)) == row["tot_lits_derived"], "Same # of lits derived"

            if len(non_timedout_instance_lits_derived) > 1:
                wrongly_non_timedout_instances.append((row["params_instance"], non_timedout_instance_lits_derived))
            if next(iter(non_timedout_instance_lits_derived)) != row["tot_lits_derived"]:
                wrongly_non_timedout.append((row["params_output"],next(iter(non_timedout_instance_lits_derived)), row["tot_lits_derived"]))

    return wrongly_non_timedout_instances, wrongly_non_timedout

def check_error_json_files(all_files):
    list_error_files = []
    for json_file in all_files:
        if not json_file.name.endswith('.json'):
            continue
        try:
            with json_file.open() as fp:
                _ = json.load(fp)
        except json.decoder.JSONDecodeError:
            print(json_file)
            list_error_files.append(json_file)
    return list_error_files

def get_base_filename(dir, ext):
    re_replace_digit = '_(\d+)'
    base_name = None
    for json_file in dir.iterdir():
        if base_name is not None:
            break
        if not json_file.name.endswith(ext):
            continue
        base_name = re.sub(ext, '', json_file.name)
        base_name = re.sub(re_replace_digit, '_', base_name)
    return base_name

def check_list_folders(
    output_folders,
    BASE_INPUT_PATH,
    BASE_OUTPUT_PATH,
    input_ext='.sbatch',
    result_ext='.json'):
    for path_config in output_folders:
        intput_folder_path, output_folder_path = Path(BASE_INPUT_PATH + path_config), Path(BASE_OUTPUT_PATH + path_config)
        input_base_name, output_base_name = None, None
        print(f"{path_config=} {intput_folder_path=} {output_folder_path=}")

        check_error_json_files([f for f in output_folder_path.iterdir() if f.name.endswith(result_ext)])
        input_base_name = get_base_filename(intput_folder_path, input_ext)
        output_base_name = get_base_filename(output_folder_path, result_ext)
        print(f"{input_base_name=} {output_base_name=}")

        print(f"""checkcount(
            input_folder={BASE_INPUT_PATH + path_config}, 
            output_folder={BASE_OUTPUT_PATH + path_config}, 
            input_base_name={input_base_name}, 
            output_base_name={output_base_name}
        )""")

        checkcount(
            input_folder=BASE_INPUT_PATH + path_config, 
            output_folder=BASE_OUTPUT_PATH + path_config, 
            input_base_name=input_base_name, 
            output_base_name=output_base_name
        )

def checkcount(input_folder, output_folder, input_base_name, output_base_name):
    input_files = [x.name for x in Path(input_folder).iterdir() if x.is_file() and x.suffix == ".sbatch" and input_base_name in x.name]
    output_files = [x.name for x in Path(output_folder).iterdir() if x.is_file() and x.suffix == ".json" and output_base_name in x.name]
    missing_files = []
    #print(f"# input {len(input_files)} output {len(output_files)} ")
    if len(input_files) != len(output_files):
        print(f"Warning: [{len(input_files) - len(output_files)}] Missing files: #input {len(input_files)} #output {len(output_files)}")
        for i in input_files:
            output_name = i.replace('.sbatch', '.json').replace(input_base_name, output_base_name)
            if output_name not in output_files:
                #print(f"sbatch {i}")
                running_info = extract_running_info(input_folder, i)
                missing_files.append((i, output_name, running_info))

    return missing_files

def extract_parameters(parameters: str):
    all_params = {}
    i = 0
    parameters = parameters.replace("python3 reuseSS.py ", "").strip()
    splitted_params = parameters.split(' ')
    while(i < len(splitted_params)):
        all_params[splitted_params[i].replace("--",'')] = splitted_params[i+1]
        i +=2

    return all_params

def extract_running_info(input_folder, input_name):
    missing_info = None
    p = Path(input_folder) / input_name
    with p.open() as fp:
        for line in fp:
             if line.startswith('python3'):
                missing_info = extract_parameters(line.rstrip().replace('\n', ''))
    return missing_info

if __name__ == "__main__":
    checkcount(INPUT_FOLDER, OUTPUT_FOLDER, SUDOKU_BASE_INPUT_NAME, SUDOKU_BASE_OUTPUT_NAME)
    checkcount(INPUT_FOLDER, OUTPUT_FOLDER, LOGIC_BASE_INPUT_NAME, LOGIC_BASE_OUTPUT_NAME)
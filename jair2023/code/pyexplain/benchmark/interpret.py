from pathlib import Path
import json
import pandas as pd

def list_json_dir(folder):
    p = Path(folder)

    # list files in dir
    files = [f for f in p.iterdir() if f.suffix == '.json']
    return files

def pbs_to_params_dir(folder):

    p = Path(folder)

    # list files in dir
    files = [f for f in p.iterdir() if f.suffix == '.pbs']
    pbs_param_dict = {}
    for f in files:
        path_file = p / f
        with path_file.open('r') as fp:
            for line in fp:
                if not line.startswith("python3"):
                    continue
                s = line.replace("python3 reuseSS.py --output ", "")
                result_json_fpath = s.split(" --puzzle ")[0]
                result_json_fpath = result_json_fpath.replace("/data/brussel/101/vsc10143/", "/home/emilio/research/")
                json_fname =    Path(result_json_fpath).name
                pbs_param_dict[json_fname] = str(p / str(f).replace(".pbs", ".json"))

    return pbs_param_dict


def read_json(f_path):
    with f_path.open('r') as fp:
        json_dict = json.load(fp)
        json_dict["filepath"] = f_path
        json_dict["filename"] = Path(f_path).name

    return json_dict

def jsonFilesToExtendedDf(jsonFiles, output_folder, param_matching=False):
    """ dictionary hierarchy
        'time' = {
            # number of hitting sets computed
            "totalTime": 0,
            # time spent in hitting set ?
            "hs": [],
            # time spent in optimising hitting set
            "opt": [],
            # time spent in sat
            "sat": [],
            # time spent in grow
            "grow": [],
            # time to find an explanation 
            "explain": [],
            # time propagating information
            "prop": [],
            # time spent in computing a MUS
            "mus":[],
            # time spent in computing a MUS
            "greedyBestStep":[],
            "preprocess":0,
            "preseeding":[],
            "postprocessing":[],
            "timeout": 0,
            "timedout": False
        },
        'numbers' = {
            # number of hitting sets computed
            "hs": [],
            # number of opt calls
            "opt": [],
            # number of sat calls
            "sat": [],
            # number of grow calls
            "grow": [],
            # number of literal explain calls skipped
            "skipped": [],
            # number of calls to propagation
            "prop": 0
        },
        'explanation': [
            'constraints': [], 'derived': [], 'cost': int}
        ]
    """
    if param_matching:
        input_folder = output_folder.replace("output/", "input/")
        pbs_params_dict = pbs_to_params_dir(input_folder)

    pd_dict = {}
    # prepopulate dictionary with good structure
    for k,v in jsonFiles[0].items():
        if not isinstance(v, dict):
            pd_dict[k] = []
            continue

        for ki, vi in v.items():
            k_name = k + "_" + ki
            pd_dict[k_name] = []

    for id, f_json in enumerate(jsonFiles):

        for k,v in f_json.items():
            if not isinstance(v, dict):
                pd_dict[k].append(v)
                continue

            if k == 'time' and not 'timedout' in v:
                pd_dict['time_timedout'].append(True if v["totalTime"] == 7200 else False)

            for ki, vi in v.items():
                k_name = k + "_" + ki
                pd_dict[k_name].append(vi)

        if param_matching:
            output_filename = f_json["filename"]
            params_path = pbs_params_dict[output_filename]
            params_f_json = read_json(Path(params_path))

            for k,v in params_f_json.items():
                key_params = "params_" + k
                if key_params not in pd_dict:
                    pd_dict[key_params] = []

                pd_dict[key_params].append(v)

    df = pd.DataFrame(pd_dict)

    return df


def folders_to_df(folders, param_matching=False):
    df = pd.DataFrame()
    for folder in folders:
        files = [read_json(f) for f in list_json_dir(folder) if f.stat().st_size > 5]
        df_folder = jsonFilesToExtendedDf(files, folder, param_matching)
        print(df_folder)
        df = df.append(df_folder)
    return df


def folder_to_pandas_df_pickle(output_folders, pickle_name):
    path_base_output_dir = "/home/emilio/research/OCUSExplain/experiments/data/output/"
    path_output_dirs = [path_base_output_dir + o for o in output_folders]
    df = folders_to_df(path_output_dirs, param_matching=True)
    df.to_pickle(pickle_name)

def best_puzzle_explanation_computer_config(df_not_timedout):
    df_min_query = df_not_timedout.groupby(["params_instance", "params_explanation_computer"])["time_totalTime"].idxmin()
    df_puzzle_computer = df_not_timedout.loc[df_min_query]

    return df_puzzle_computer

def best_puzzle_config(df_not_timedout):
    df_min_query = df_not_timedout.groupby(["params_instance"])["time_totalTime"].idxmin()
    df_puzzle_computer = df_not_timedout.loc[df_min_query]

    return df_puzzle_computer


def pickle_to_research_questions(pickle_path):
    df = pd.read_pickle(pickle_path)
    all_column_names = ['time_totalTime', 'time_hs', 'time_opt', 'time_sat', 'time_grow', 'time_explain', 'time_prop', 'time_mus', 'time_greedyBestStep', 'time_preprocess', 'time_preseeding', 'time_postprocessing', 'time_timedout', 'numbers_hs', 'numbers_opt', 'numbers_sat', 'numbers_grow', 'numbers_skipped', 'numbers_prop', 'explanation', 'filepath', 'filename', 'params_output', 'params_instance', 'params_timeout', 'params_explanation_computer', 'params_grow', 'params_maxsatpolarity', 'params_interpretation', 'params_weighing', 'params_reuse_SSes', 'params_sort_literals', 'params_filepath', 'params_filename']
    col_inst_time_config = ["params_instance", 'params_explanation_computer', "time_totalTime",'params_grow', 'params_maxsatpolarity', 'params_interpretation', 'params_weighing', 'params_reuse_SSes', 'params_sort_literals']


    # best configuration for all epxlnaation computers
    df_not_timedout = df[(df["time_totalTime"] < 7200) & (df["time_totalTime"] > 0)]

    df_not_timedout_not_MUS = df_not_timedout[df_not_timedout["params_explanation_computer"] != "MUS"]
    df_not_timedout_OCUS = df_not_timedout[df_not_timedout["params_explanation_computer"] == "OCUS"]

    # Best configuration for all explanation computer and all puzzles
    df_best_puzzle_computer_config = best_puzzle_explanation_computer_config(df_not_timedout)[col_inst_time_config]

    # Best configuraiton for all puzzles
    df_best_puzzle_config = best_puzzle_config(df_not_timedout)[col_inst_time_config]
    df_best_puzzle_config_not_MUS = best_puzzle_config(df_not_timedout_not_MUS)[col_inst_time_config]
    df_best_puzzle_config_OCUS = best_puzzle_config(df_not_timedout_OCUS)[col_inst_time_config]

    print(df_best_puzzle_config)
    print(df_best_puzzle_config_not_MUS)
    print(df_best_puzzle_config_OCUS)

    # generate first research questions

    # generate second research question


if __name__ == "__main__":
    output_folders = ["2021032219"]
    pickle_name ="pickles/2021032219.pkl"
    # folder_to_pandas_df_pickle(output_folders, pickle_name)
    pickle_to_research_questions(pickle_name)


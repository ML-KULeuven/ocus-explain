from pathlib import Path
import json
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
from pyexplain.solvers.params import ExplanationComputer, Grow, Interpretation, DisjointMCSes, Weighing

# functions for reading and extract dataframe from json files
def list_json_dir(folder):
    p = Path(folder)

    # list files in dir
    files = [f for f in p.iterdir() if f.suffix == '.json']
    return files

def replace_none(json_dict):
    new_json_dict = dict(json_dict)
    for k, v in json_dict.items():
        if isinstance(v, dict):
            new_json_dict[k] = replace_none(v)
        elif v is None:
            new_json_dict[k] = "ignore"

    return new_json_dict

def read_json(f_path):
    json_dict = dict()
    with f_path.open('r') as fp:
        try:
            json_dict = json.load(fp)
        except Exception as e:
            #print(f"File={f_path} \n{e}")
            json_dict["filepath"] = f_path
            json_dict["filename"] = Path(f_path).name
            return json_dict

    return replace_none(json_dict)

def column_all_same_values(s):
    # check all values in a column are the same
    a = s.to_numpy() # s.values (pandas<0.24)
    return (a[0] == a).all()

def json_files_to_extended_df(jsonFiles):
    """
        Dictionary hierarchy

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
    pd_dict = defaultdict(list)
    # prepopulate dictionary with good structure

    for f_json in jsonFiles:
        for k,v in f_json.items():
            if not isinstance(v, dict):
                pd_dict[k] = []
                continue

            for ki, vi in v.items():
                k_name = k + "_" + ki
                if k_name not in pd_dict:
                    pd_dict[k_name] = []

    for f_json in jsonFiles:
        filled_keys = []
        #if '2022021717/RQ3_DEMYSTIFY_PUZZLES__results_897.json' in f_json["params"]["output"]:
        #    print(f_json)

        for k,v in f_json.items():
            if not isinstance(v, dict):
                pd_dict[k].append(v)
                filled_keys.append(k)
                continue

            if k == 'time' and not 'timedout' in v:
                pd_dict['time_timedout'].append(True if ((v["totalTime"] >= 3600) or (len(v["explanation"])==0)) else False)

                filled_keys.append('time_timedout')

            for ki, vi in v.items():
                k_name = k + "_" + ki
                pd_dict[k_name].append(vi)
                filled_keys.append(k_name)

        if pd_dict["time_totalTime"][-1] == 0:
            pd_dict["time_totalTime"][-1] += 0.01
        default_key_val = {
            "time_opt": [0],
            "time_sat": [0],
            "time_grow":[0],
            "time_disj_mcs":[0],
            "numbers_#opt":[0],
            "numbers_#sat":[0],
            "numbers_#grow":[0],
            "numbers_#hs":[0],
            "numbers_#hs_disj_mcs": [0],
            "numbers_#disj_mcs": [0],
            "time_remaining": [0]
        }

        for k in pd_dict:
            if k not in filled_keys:
                if k in default_key_val:
                    pd_dict[k].append(default_key_val[k])
                else:
                    pd_dict[k].append("ignore")

    df = pd.DataFrame(pd_dict)
    # print(df)
    df["time_timedout_initial"] = df.apply(lambda row: row["time_timedout"], axis=1)
    df["time_timedout"] = df.apply(lambda row: True if ((row["time_totalTime"] >= 3600) or (len(row["explanation"])==0)) else False, axis=1)
    df["time_totalTime_initial"] = df.apply(lambda row: row["time_totalTime"],  axis=1)
    df["time_totalTime"] = df.apply(
        lambda row: row["params_timeout"] if (row["time_timedout"] or (len(row["explanation"])==0)) else row["time_totalTime"],
        axis=1)

    return df

def folder_to_pandas_df_pickle(output_folders, n=None):

    if n:
        files = [read_json(f) for folder in output_folders for f in list_json_dir(folder)[:n]  if f.stat().st_size > 5]
    else:
        files = [read_json(f) for folder in output_folders for f in list_json_dir(folder) if f.stat().st_size > 5]

    df_folder = json_files_to_extended_df(files)
    df = pd.DataFrame(df_folder)
    return df


# ensure totTime is timeout
def cumul_expl_time(row):
    expl_time = row["texpl"]
    cumul_expl = []
    cumul_time = 0

    for t in expl_time:
        cumul_time += t
        cumul_expl.append(cumul_time)

    if row["timeout"]:
        cumul_expl.append(row["params_timeout"])

    return cumul_expl

def cumul_lits_derived(row):
    expls = row["explanation"]
    cumul_lits = 0
    cumul_lit_seq = []

    for explanation in expls:
        n_lits_derived = len(explanation["derived"])
        cumul_lits += n_lits_derived
        cumul_lit_seq.append(cumul_lits)
    return cumul_lit_seq

def lits_derived(row):
    # print(row)
    if not isinstance(row["explanation"], list):
        print(row["filepath"])
    expls = row["explanation"]
    lit_seq = []
    for explanation in expls:
        # print(explanation) 
        n_lits_derived = len(explanation["derived"])
        lit_seq.append(n_lits_derived)
    return lit_seq

def joint_lits_time(row):
    expls = row["expl_seq"]
    texpl = row["texpl"]
    lit_seq = []
    cumul_time = 0
    for explanation, time_expl  in zip(expls, texpl):
        cumul_time += time_expl
        n_lits_derived = len(explanation["derived"])
        lit_seq.append((cumul_time, n_lits_derived))
    
    if row["timeout"]:
        lit_seq.append((row["params_timeout"], 0))
    return lit_seq

def rename_grow_config(row):
    grow_renaming = {
        Grow.MAXSAT.name: "MaxSAT",
        Grow.SAT.name: "SAT",
        Grow.DISJ_MCS.name: "Disj.MCSes",
        Grow.SUBSETMAX.name: "Greedy-Sat",
        Grow.DISABLED.name: "No Grow",
        Grow.CONSTRAINT_DISJ_MCS.name: "Constr. MCSes",
        Grow.CORR_GREEDY.name: "Greedy MCSes",
        Grow.CORRECTION_SUBSETS_SAT.name: "SAT MCSes",
        Grow.CORRECTION_SUBSETMAX_SAT.name: "SUBSETMAX SAT MCSes",
        '': "",
        'ignore': "No Grow",
        None: "No Grow",
    }

    weights_renaming = {
        Weighing.POSITIVE.name: "Pos.",
        Weighing.INVERSE.name: "Inv.",
        Weighing.UNIFORM.name: "Unif.",
        'ignore': "",
        '': "",
        None: "",
    }

    interpretation_renaming = {
        # Interpretation.INITIAL.name: "I_0",
        # Interpretation.ACTUAL.name: "I",
        # Interpretation.FULL.name: "I + (-Iend minus -I)",
        # Interpretation.FINAL.name: "Iend",
        Interpretation.INITIAL.name: "Initial",
        Interpretation.ACTUAL.name: "Actual",
        Interpretation.FULL.name: "Full",
        Interpretation.FINAL.name: "Final",
        'ignore': "",
        '': "",
        None: "",
    }

    if row["params_grow"] in [Grow.SAT.name, Grow.DISABLED.name, 'ignore', None]:
        return grow_renaming[row["params_grow"]]

    elif row["params_grow"] not in grow_renaming:
        raise Exception("Wrong grow renaming: " + row["params_grow"])


    grow_config_list = [
        grow_renaming[row["params_grow"]],
        interpretation_renaming[row["params_interpretation"]],
        weights_renaming[row["params_weighing"]]
    ]

    # ignore the empty string
    grow_config_list = [g for g in grow_config_list if len(g) > 0]

    return " + ".join(grow_config_list)

def average_lits_derived_time(row, penalty=3600, max_num_lits_derived=250):
    
    avg_lits_derived_times = [(0, 0)]
    j = 1
    tot_time = 0
    for lits_derived, texpl in zip(row["lits_derived"], row["time_cumul_explain"]):
        for i in range(lits_derived):
            avg_lits_derived_times.append((j,texpl))
            j+= 1
        tot_time = texpl

    if row["time_timedout"]:
        for k in range(j, max_num_lits_derived+1):
            avg_lits_derived_times.append((k, penalty))

    elif j < max_num_lits_derived:
        for i in range(j, max_num_lits_derived + 1):
            avg_lits_derived_times.append((i, tot_time))

    return avg_lits_derived_times

def family_puzzle_instance(instance):
    if instance.startswith('binairo'):
        return 'binairo'
    elif instance.startswith('killersudoku'):
        return 'killersudoku'
    elif instance.startswith('kakuro'):
        return 'kakuro'
    elif instance.startswith('garam'):
        return 'garam'
    elif instance.startswith('kakurasu'):
        return 'kakurasu'
    elif instance.startswith('miracle'):
        return 'miracle'
    elif instance.startswith('nonogram'):
        return 'nonogram'
    elif instance.startswith('skyscrapers'):
        return 'skyscrapers'
    elif instance.startswith('star-battle'):
        return 'star-battle'
    elif instance.startswith('sudoku_sudokuwiki'):
        return 'sudoku_sudokuwiki'
    elif instance.startswith('sudoku'):
        return 'sudoku'
    elif instance.startswith('tents_tents'):
        return 'tents_tents'
    elif instance.startswith('thermometer'):
        return 'thermometer'
    elif instance.startswith('x-sums'):
        return 'x-sums'
    else:
        return 'logic'

def data_set_puzzle_instance(instance):
    demystify_puzzles = [
        'binairo', 'killersudoku', 'kakuro', 'garam', 'kakurasu', 'miracle',
        'nonogram', 'skyscrapers', 'star-battle', 'sudoku_sudokuwiki', 'tents_tents'
        'thermometer', 'x-sums'
    ]

    if any(instance.startswith(p) for p in demystify_puzzles):
        return 'DEMYSTIFY'
    else:
        return 'OCUS-EXPLAIN'

def mus_size(expl_seq):
    sizes = []
    for expl in expl_seq:
        size = len(expl["constraints"]) + 1
        sizes.append(size)

    return sizes

def cumulative_lits_derived_time(df):
    """Given a specific configuration plot the cumulative explanation time
    with respect to the number of ltierals derived."""
    assert len(set(df["params_explanation_computer"])) == 1, "making sure there is only 1 config"
    assert len(set(df["params_instance"])) == 10, "Making sure we have all puzzles"
    assert len(df) == 10, "Only 10 puzzle configs"
    x = [0]
    y = [0]
    times_lits_derived = []

    # one whole list
    for id, row in df.iterrows():
        times_lits_derived += row["joint_lits_time"]

    # sorting on cumulative time
    times_lits_derived.sort(key=lambda x: x[0])
    n_cumul_lits = 0

    # computing the 
    for (t, nlit) in times_lits_derived:
        n_cumul_lits += nlit
        y.append(t)
        x.append(n_cumul_lits)

    return x, y

def cumulative_expl_time(df):
    """Given a specific configuration plot the cumulative explanation time
    with respect to the number of ltierals derived."""
    assert len(set(df["params_explanation_computer"])) == 1, "making sure there is only 1 config"
    assert len(set(df["params_instance"])) == 10, "Making sure we have all puzzles"
    assert len(df) == 10, "Only 10 puzzle configs"

    expls_derived = [0]

    for id, row in df.iterrows():
        expls_derived += row["cumul_expl"]

    expls_derived.sort()
    x = list(range(len(expls_derived)))

    return x, expls_derived

def config_cumulative_exec_time(df):
    df_cumul = df.groupby(by=["params_explanation_computer"])["cumul_explain_time"].apply(
        lambda x : sorted(x.sum())
    ).reset_index().rename(columns={'cumul_explain_time':'cumul_explain_time'})

    df_cumul["cumul_explain_step"] = df_cumul.apply(
                lambda row: [x for x in range(1, len(row["cumul_explain_time"])+1)]
        , axis=1)

    return df_cumul

def rename_explanation_config(row):

    d_expl_config_renaming = {
        ExplanationComputer.MUS.name: "MusX",
        ExplanationComputer.OUS_SS.name: "OUSb",
        ExplanationComputer.OUS_NO_OPT.name: "OUS",
        ExplanationComputer.OUS_INCREMENTAL_NAIVE.name: "OUSb+Lit. Incr. HS",
        ExplanationComputer.OUS_INCREMENTAL_NAIVE_PARALLEL.name: "OUSb+Iterative+Lit. Incr. HS",
        ExplanationComputer.OUS_NAIVE_PARALLEL.name: "OUSb+Iterative",
        ExplanationComputer.OUS_INCREMENTAL_SHARED.name: "OUSb+Lit. Incr. HS+Shared SS. caching",
        ExplanationComputer.OCUS.name: "OCUS+Incr. HS",
        ExplanationComputer.OCUS_NOT_INCREMENTAL.name: "OCUS",
        ExplanationComputer.OPTUX_HITMAN.name: "OptUx",
        '': "",
    }

    expl_config = row["params_explanation_computer"]
    reuse_sses = ("+SS. caching" if row["params_reuse_SSes"] else "")

    if expl_config not in d_expl_config_renaming:
        raise Exception(str(expl_config))

    s = d_expl_config_renaming[expl_config]
    s += reuse_sses

    return s

def rename_full_explanation_config(row):

    renaming_disj_mcs = {
        DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY.name: "Bootstrap Disj. MCS once",
        DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL.name:"Bootstrap Disj. MCS",
        DisjointMCSes.DISABLED.name: "",
        None: "",
        '': "",
        "ignore":""
    }

    d_expl_config_renaming = {
        ExplanationComputer.MUS.name: "MusX",
        ExplanationComputer.OUS_SS.name: "OUSb",
        ExplanationComputer.OUS_NO_OPT.name: "OUS",
        ExplanationComputer.OUS_INCREMENTAL_NAIVE.name: "OUSb+Lit. Incr. HS",
        ExplanationComputer.OUS_NAIVE_PARALLEL.name: "OUSb+Iterative",
        ExplanationComputer.OUS_INCREMENTAL_NAIVE_PARALLEL.name: "OUSb+Iterative+Lit. Incr. HS",
        ExplanationComputer.OUS_INCREMENTAL_SHARED.name: "OUSb+Lit. Incr. HS+Shared SS. caching",
        ExplanationComputer.OCUS.name: "OCUS+Incr. HS",
        ExplanationComputer.OCUS_NOT_INCREMENTAL.name: "OCUS",
        ExplanationComputer.OPTUX_HITMAN.name: "OptUx",
        '': "",
    }

    expl_config = row["params_explanation_computer"]
    mcs_config = renaming_disj_mcs[row["params_disjoint_mcses"]]
    grow_config = ("+"+row["params_grow"]) if row["params_grow"] in ["DISJ_MCS", "MAXSAT"] else ""
    sorting = ("+sort" if row["params_sort_literals"] else "")
    reuse_sses = ("+SS. caching" if row["params_reuse_SSes"] else "")
    disj_mcs_enum_disabled = ("+Disj.MCS-Enum" if row["params_disable_disjoint_mcses"] else "")

    if expl_config not in d_expl_config_renaming:
        raise Exception(str(expl_config))

    s = d_expl_config_renaming[expl_config]

    if expl_config == "OptUx":
        s += disj_mcs_enum_disabled

    s += reuse_sses
    s += sorting
    s += grow_config
    s += mcs_config

    return s

def enhance_dataframe(df):
    df["instance_family"] = df.apply(lambda row: family_puzzle_instance(row["params_instance"]), axis=1)
    df["instance_dataset"] = df.apply(lambda row: data_set_puzzle_instance(row["params_instance"]), axis=1)
    df["lits_derived"] = df.apply(lambda row: lits_derived(row), axis=1)
    df["tot_lits_derived"] = df.apply(lambda row: sum(row["lits_derived"]), axis=1)

    df["average_lits_derived_time"] = df.apply(lambda row: average_lits_derived_time(row, penalty=3600, max_num_lits_derived=max(df["tot_lits_derived"])), axis=1)
    # print("max_num lits:", max(df["tot_lits_derived"]))
    # df["average_lits_derived_time"] = df.apply(lambda row: average_lits_derived_time(row, penalty=row["params_timeout"]), axis=1)
    df['cumul_explain_time'] = df.apply(
        lambda row: [sum(row["time_explain"][:x]) for x in range(1, len(row["time_explain"])+1)]
    , axis=1)
    df['tot_time_explain'] = df.apply( lambda row: sum(row["time_explain"]), axis=1)
    df["params_grow_config"] = df.apply(lambda row: rename_grow_config(row), axis=1)
    df["params_full_explanation_config"] = df.apply(lambda row: rename_full_explanation_config(row), axis=1)
    df["params_explanation_config"] = df.apply(lambda row: rename_explanation_config(row), axis=1)

    return df


def rename_grow_sat_mip_explanation_config(expl_config):
    from pyexplain.solvers.params import ExplanationComputer

    renamed_config = {
        "MUS": "MUS",
        "OUS_SS": "OUS+Subsets",
        "OUS_NO_OPT": "OUS",
        "OUS_INCREMENTAL_NAIVE": "Greedy OUS+Incr.",
        "OUS_INCREMENTAL_NAIVE_PARALLEL": "Iterated OUS+Incr.",
        "OUS_NAIVE_PARALLEL": "Iterated OUS",
        "OUS_INCREMENTAL_SHARED": "OUS+Incr.+Shared Subsets",
        "OCUS": "OCUS+Incr.",
        "OCUS_NOT_INCREMENTAL": "OCUS"
    }
    if expl_config in renamed_config:

        return renamed_config[expl_config]

    return expl_config

def rename_corr_explanation_config(row):
    name_expl_config = row["renamed_explanation_config"]

    grow_renaming = {
        Grow.MAXSAT.name: "+MaxSAT",
        Grow.DISJ_MCS.name: "+CorrSubsets",
        Grow.SAT.name: "+SAT",
        Grow.SUBSETMAX.name: "+Greedy SAT",
        Grow.DISABLED.name: "+No grow",
        Grow.CORR_GREEDY.name: "+Greedy CorrSubsets",
        Grow.CORRECTION_SUBSETS_SAT.name:"+SAT CorrSubsets",
        Grow.CORRECTION_SUBSETMAX_SAT.name:"+SUSETMAX SAT CorrSubsets",
        "ignore":"",
        None:"",
        "":"",
    }

    disj_renaming = {
        DisjointMCSes.DISABLED.name: "",
        DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY.name: "+Corr. Subsets Boostrap Once",
        DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL.name: "+Corr. Subsets Boostrap All",
        DisjointMCSes.GREEDY_CORR_BOOTSTRAP_ALL.name: "+Greedy Corr. Subsets Boostrap All",
        DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY.name: "+Greedy Corr. Subsets Boostrap Once",
        "PREPROCESSING_ONLY": "+Corr. Subsets Boostrap Once",
        "BOOTSTRAP_ALL": "+Corr. Subsets Boostrap All",
        "ignore":"",
        None:"",
        "":"",
    }
    new_name_expl_config = name_expl_config
    new_name_expl_config += grow_renaming[row["params_grow"]]
    new_name_expl_config += disj_renaming[row["params_disjoint_mcses"]]

    return new_name_expl_config


# def average_lits_derived_time(row, penalty=3600, max_num_lits_derived=250):
    
#     avg_lits_derived_times = [(0, 0)]
#     j = 1
#     tot_time = 0
#     for lits_derived, texpl in zip(row["lits_derived"], row["time_explain"]):
#         tot_time += texpl
#         for i in range(lits_derived):
#             avg_lits_derived_times.append((j,tot_time))
#             j+= 1

#     if row["time_timedout"]:
#         for k in range(j, max_num_lits_derived+1):
#             avg_lits_derived_times.append((k, penalty))

#     elif j < max_num_lits_derived:
#         for i in range(j, max_num_lits_derived + 1):
#             avg_lits_derived_times.append((i, tot_time))

#     return avg_lits_derived_times

def total_expl_cost(explanation_sequence):
    cost = 0
    if explanation_sequence is None or len(explanation_sequence) == 0:
        return cost

    for expl in explanation_sequence:
        cost += expl["cost"]
    return cost

def msg_enhance_df(df):
    df["instance_family"] = df.apply(lambda row: family_puzzle_instance(row["params_instance"]), axis=1)
    df["instance_dataset"] = df.apply(lambda row: data_set_puzzle_instance(row["params_instance"]), axis=1)
    df["lits_derived"] = df.apply(lambda row: lits_derived(row), axis=1)
    df["tot_lits_derived"] = df.apply(lambda row: sum(row["lits_derived"]), axis=1)

    df["average_lits_derived_time"] = df.apply(lambda row: average_lits_derived_time(row, penalty=3600, max_num_lits_derived=max(df["tot_lits_derived"])), axis=1)

    df["total_expl_cost"]  = df.apply(lambda row: total_expl_cost(row["explanation"]), axis=1)
    df["params_grow_config"] = df.apply(lambda row: rename_grow_config(row), axis=1)
    df["params_full_explanation_config"] = df.apply(lambda row: rename_full_explanation_config(row), axis=1)
    df["params_explanation_config"] = df.apply(lambda row: rename_explanation_config(row), axis=1)


    df["instance_type"] = df.apply(lambda row: "sudoku" if ("sudoku" in row["params_instance"]) else "logic", axis=1)
    df["tot_time_opt"] = df.apply(lambda row: sum(row["time_opt"]) if "time_opt" in row else 0, axis=1)
    df["tot_time_sat"] = df.apply(lambda row: sum(row["time_sat"]) if "time_sat" in row else 0, axis=1)
    df["tot_time_grow"] = df.apply(lambda row: sum(row["time_grow"])  if "time_grow" in row else 0, axis=1)
    df["tot_time_disj_mcs"] = df.apply(lambda row: sum(row["time_disj_mcs"])  if "time_disj_mcs" in row else 0, axis=1)
    df["tot_time_remaining"] = df.apply(lambda row: 0 if "time_remaining" not in row else sum(row["time_remaining"]), axis=1)
    df["tot_time_explain"] = df.apply(lambda row: sum(row["time_explain"]) if not row["time_timedout"] else row["params_timeout"], axis=1)
    #### ignoring time remaining!
    df["tot_time_ous"] = df.apply(lambda row: row["tot_time_opt"] + row["tot_time_sat"]+ row["tot_time_grow"]+ row["tot_time_disj_mcs"], axis=1)

    df["%time_opt"] = df.apply(
        lambda row: round(100 * row["tot_time_opt"]/row['tot_time_explain'],2) if row['tot_time_explain'] > 0 else 0, axis=1)
    df["%time_sat"] = df.apply(
        lambda row: round(100 * row["tot_time_sat"]/row['tot_time_explain'],2) if row['tot_time_explain'] > 0 else 0, axis=1)
    df["%time_grow"] = df.apply(
        lambda row: round(100 * row["tot_time_grow"]/row['tot_time_explain'],2) if row['tot_time_explain'] > 0 else 0, axis=1)
    df["%time_disj_mcs"] = df.apply(
        lambda row: round(100 * row["tot_time_disj_mcs"]/row['tot_time_explain'],2) if row['tot_time_explain'] > 0 else 0, axis=1)
    df["%time_remaining"] = df.apply(
        lambda row: round(
            100 * (1-(row["tot_time_disj_mcs"] + row["tot_time_opt"] + row["tot_time_sat"] + row["tot_time_grow"] + row["tot_time_remaining"])/row['time_totalTime']),
        2), axis=1)

    df["%time_opt2"] = df.apply(
        lambda row: round(100 * row["tot_time_opt"]/row['tot_time_ous'],2) if row['tot_time_ous'] > 0 else 0, axis=1)
    df["%time_sat2"] = df.apply(
        lambda row: round(100 * row["tot_time_sat"]/row['tot_time_ous'],2) if row['tot_time_ous'] > 0 else 0, axis=1)
    df["%time_grow2"] = df.apply(
        lambda row: round(100 * row["tot_time_grow"]/row['tot_time_ous'],2) if row['tot_time_ous'] > 0 else 0, axis=1)
    df["%time_disj_mcs2"] = df.apply(
        lambda row: round(100 * row["tot_time_disj_mcs"]/row['tot_time_ous'],2) if row['tot_time_ous'] > 0 else 0, axis=1)
    df["%time_remaining2"] = df.apply(
        lambda row: round(
            (100 * (row["tot_time_remaining"])/row['tot_time_ous']) if row['tot_time_ous'] > 0 else 0,
        2), axis=1)

    df["tot_n_opt"] = df.apply(lambda row: sum(row["numbers_#opt"]) if "numbers_#opt" in row else 0, axis=1)
    df["tot_n_sat"] = df.apply(lambda row: sum(row["numbers_#sat"]) if "numbers_#sat" in row else 0, axis=1)
    df["tot_n_grow"] = df.apply(lambda row: sum(row["numbers_#grow"]) if "numbers_#grow" in row else 0, axis=1)
    df["tot_n_hs"] = df.apply(lambda row: sum(row["numbers_#hs"]) if "numbers_#hs" in row else 0, axis=1)
    df["tot_n_hs_disj_mcs"] = df.apply(lambda row: sum(row["numbers_#hs_disj_mcs"]) if "numbers_#hs_disj_mcs" in row else 0, axis=1)

    if "numbers_#disj_mcs" in df.columns:
        df["tot_n_disj_mcs"] = df.apply(lambda row: sum(row["numbers_#disj_mcs"]), axis=1)
    else:
        df["tot_n_disj_mcs"] = df.apply(lambda row: 0, axis=1)


    df["avg_n_hs"] = df.apply(lambda row: 0 if ((row['tot_n_disj_mcs'] + row['tot_n_grow']) == 0) else row["tot_n_hs"]/(row['tot_n_disj_mcs'] + row['tot_n_grow']) , axis=1)
    df["avg_n_hs_disj_mcs"] = df.apply(lambda row: 0 if row['tot_n_disj_mcs'] == 0 else row["tot_n_hs_disj_mcs"]/row['tot_n_disj_mcs'], axis=1)

    df["lits_derived"] = df.apply(lambda row: lits_derived(row), axis=1)
    df["tot_lits_derived"] = df.apply(lambda row: sum(row["lits_derived"]), axis=1)

    df["average_lits_derived_time"] = df.apply(lambda row: average_lits_derived_time(row, penalty=3600, max_num_lits_derived=max(df["tot_lits_derived"])), axis=1)
    df["renamed_explanation_config"]= df.apply(lambda row: rename_grow_sat_mip_explanation_config(row["params_explanation_computer"]), axis=1)
    
    df["avg_t_explain"]= df.apply(lambda row: np.mean(row["time_explain"]), axis=1)
    df["max_t_explain"]= df.apply(lambda row: np.max(row["time_explain"]) if len(row["time_explain"]) > 0 else 0, axis=1)
    df["min_t_explain"]= df.apply(lambda row: np.min(row["time_explain"]) if len(row["time_explain"]) > 0 else 0, axis=1)
    df["n_expls"]= df.apply(lambda row: len(row["time_explain"]), axis=1)
    return df


def corr_enhance_df(df):
    df = msg_enhance_df(df)
    df["tot_time_remaining"] = df.apply(lambda row: sum(row["time_remaining"]) if "time_remaining" in row else 0, axis=1)
    
    df["%time_remaining_ocus"] = df.apply(lambda row: round(100 * row["tot_time_remaining"]/row['time_totalTime'],2), axis=1)
    df["corr_explanation_config"]= df.apply(lambda row: rename_corr_explanation_config(row), axis=1)
    df["incremental"] = df.apply(lambda row: True if ("Incr" in row["corr_explanation_config"]) else False, axis=1)

    return df

def table_group_summarize(df_grouped):
    
    df_temp = df_grouped.agg(
        ## OPT
        avg_opt=("%time_opt" , lambda x: round(np.mean(x), 2)),
        std_opt=("%time_opt" , lambda x: round(np.std(x), 2)),
        tot_t_opt=("tot_time_opt" , lambda x: sum(x)),
        tot_n_opt=("tot_n_opt" , lambda x: sum(x)),
        avg_n_opt=("tot_n_opt" , lambda x: round(np.mean(x))),
        ## SAT
        avg_sat=("%time_sat" , lambda x: round(np.mean(x), 2)),
        std_sat=("%time_sat" ,lambda x: round(np.std(x), 2)),
        tot_t_sat=("tot_time_sat" , lambda x: sum(x)),
        avg_n_sat=("tot_n_sat" , lambda x: round(np.mean(x))),
        tot_n_sat=("tot_n_sat" , lambda x: sum(x)),
        ## GROW
        avg_grow=("%time_grow" , lambda x: round(np.mean(x), 2)),
        std_grow=("%time_grow" , lambda x: round(np.std(x), 2)),
        tot_t_grow=("tot_time_grow" , lambda x: sum(x)),
        tot_n_grow=("tot_n_grow" , lambda x: sum(x)),
        avg_n_grow=("tot_n_grow" , lambda x: round(np.mean(x))),
        ## DISJ MCS
        avg_disj_mcs=("%time_disj_mcs" , lambda x: round(np.mean(x), 2)),
        std_disj_mcs=("%time_disj_mcs" , lambda x: round(np.std(x), 2)),
        tot_t_disj_mcs=("tot_time_disj_mcs" , lambda x: sum(x)),
        tot_n_disj_mcs=("tot_n_disj_mcs" , lambda x: sum(x)),
        avg_n_disj_mcs=("tot_n_disj_mcs" , lambda x: round(np.mean(x))),

        tot_n_hs=("tot_n_hs"  , lambda x: sum(x)),
        
        avg_n_hs=("avg_n_hs" , lambda x: round(np.mean(x), 2)),
        avg_n_hs_disj_mcs=("avg_n_hs_disj_mcs" , lambda x: round(np.mean(x), 2)),
        ## Remainign
        avg_other=("%time_remaining" , lambda x: round(np.mean(x), 2)),
        std_other=("%time_remaining" , lambda x: round(np.std(x), 2)),
        
        avg_remaining_ocus=("%time_remaining_ocus" , lambda x: round(np.mean(x), 2)),
        std_remaining_ocus=("%time_remaining_ocus" , lambda x: round(np.std(x), 2)),
        ### TOtal time
        tot_time=("tot_time_explain" , lambda x: sum(x)),
    ).reset_index()

    df_temp["avg_t_opt"] = df_temp.apply(
        lambda row: round(0 if row["tot_n_opt"] == 0 else row["tot_t_opt"]/row['tot_n_opt'], 4), axis=1
    )
    df_temp["avg_t_sat"] = df_temp.apply(
        lambda row: round(0 if row["tot_n_sat"] == 0 else row['tot_t_sat']/row['tot_n_sat'], 4), axis=1
    )
    df_temp["avg_t_grow"] = df_temp.apply(
        lambda row: round(0 if row["tot_n_grow"] == 0 else row['tot_t_grow']/row['tot_n_grow'], 4), axis=1
    )    
    df_temp["avg_t_disj_mcs"] = df_temp.apply(
        lambda row: round(0 if row["tot_n_disj_mcs"] == 0 else row['tot_t_disj_mcs']/row['tot_n_disj_mcs'], 4), axis=1
    )    

    for k in ["opt", "sat", "grow", "disj_mcs", "other", "remaining_ocus"]:
        df_temp[k] = df_temp.apply(lambda row: None, axis=1)
        for index,row in df_temp.iterrows():        
            if row["avg_"+k] != 0:
                df_temp.at[index,k]= f'{row["avg_"+k]}% [+/- {row["std_"+k]}%]'
            else:
                df_temp.at[index,k] = "---"
    df_temp["expl_config"] = df_temp.apply(lambda row: row["renamed_explanation_config"], axis=1)
    return df_temp

def explanation_time_quantile(t_expl, quantile):
    return round(np.quantile(t_expl, quantile), 2)



def stats_expls_times(df):
    #df["config"] = df.apply(lambda row: latex_rename_corr_expl_config(row["corr_explanation_config"]), axis=1)
    df["avg_t_expl"] = df.apply(lambda row: round(np.mean(row["t_expl"]),2), axis=1)
    df["med_t_expl"] = df.apply(lambda row: np.median(row["t_expl"]), axis=1)
    df["n_expl"] = df.apply(lambda row: len(row["t_expl"]), axis=1)
    df["min_t_expl"] =df.apply(lambda row: np.min(row["t_expl"]), axis=1)
    df["max_t_expl"] =df.apply(lambda row: np.max(row["t_expl"]), axis=1)
    #df["tot_expl"] =df.apply(lambda row: sum(row["tot_time"]), axis=1)
    df["tot_time (s)"] =df.apply(lambda row: round(row["tot_time"]), axis=1)
    df["time_to_first_expl"] =df.apply(lambda row: row["t_expl"][0], axis=1)
    df["q_25"] =df.apply(lambda row: explanation_time_quantile(row["t_expl"], quantile=0.25), axis=1)
    df["q_50"] =df.apply(lambda row: explanation_time_quantile(row["t_expl"], quantile=0.50), axis=1)
    df["q_75"] =df.apply(lambda row: explanation_time_quantile(row["t_expl"], quantile=0.75), axis=1)
    df["q_95"] =df.apply(lambda row: explanation_time_quantile(row["t_expl"], quantile=0.95), axis=1)
    df["q_98"] =df.apply(lambda row: explanation_time_quantile(row["t_expl"], quantile=0.98), axis=1)
    df["q_100"] =df.apply(lambda row: explanation_time_quantile(row["t_expl"], quantile=1), axis=1)
    return df

def mean_ignore_zeros(x):
    l = [xi for xi in x if xi != 0 and xi != 0.0]
    #print(l)
    if len(l) == 0:
        return 0
    return sum(l)/len(l)

# Generate the isntances with only Maxsat grow
from datetime import datetime
from pathlib import Path
import json
from generate_params import RQ3b_corr_subsets, all_logic_puzzles, all_params_to_sbatch_files, demystify_puzzles, exect_ime_given_instances, puzzle_funs, all_sudokus, rq2, rq2c_paper_configs, rq3

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

### EPXERIMENT RQ2
RQ2c_DEMYSTIFY_PUZZLES = "RQ2c_DEMYSTIFY_PUZZLES/" + CURRENT_HOUR

RQ2c_DEMYSTIFY_PUZZLES_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + RQ2c_DEMYSTIFY_PUZZLES
RQ2c_DEMYSTIFY_PUZZLES_LOCAL_TEST_OUTPUT_FOLDER = PYEXPLAIN_LOCAL_FOLDER + "pyexplain/benchmark/test/"
RQ2c_DEMYSTIFY_PUZZLES_HPC_OUTPUT_FOLDER = HPC_OUTPUT + RQ2c_DEMYSTIFY_PUZZLES

RQ2c_DEMYSTIFY_PUZZLES_LOCAL_INPUT_FOLDER = LOCAL_INPUT + RQ2c_DEMYSTIFY_PUZZLES
RQ2c_DEMYSTIFY_PUZZLES_HPC_INPUT_FOLDER = HPC_INPUT + RQ2c_DEMYSTIFY_PUZZLES

base_fname_RQ2c_DEMYSTIFY_PUZZLES = "RQ2c_DEMYSTIFY_PUZZLES_"

# REMAINING INSTANCES
# REMAINING INSTANCES
explained_demystify_instances= ['garam_garam_10_garam-diff-201120.param.json',
 'garam_garam_11_garam-tut.param.json',
 'garam_garam_1_garam-adv-201120.param.json',
 'garam_garam_2_garam-master-201120.param.json',
 'garam_garam_3_garam-beg-201120.param.json',
 'garam_garam_4_garam-fiend-201120.param.json',
 'garam_garam_5_garam-exp-201120.param.json',
 'garam_garam_7_garam-easy-201120.param.json',
 'garam_garam_8_garam-medium-201120.param.json',
 'garam_garam_9_garam-vdiff-201120.param.json',
 'kakuro_kakuro_0_conceptispuzzles.param.json',
 'kakuro_kakuro_1_2-definitions-intersection.param.json',
 'kakuro_kakuro_3_1-row-col-restrictions.param.json',
 'killersudoku_killersudoku_0_crackingkillersudoku.param.json',
 'killersudoku_killersudoku_10_6-7-innies-and-outies.param.json',
 'killersudoku_killersudoku_11_5-6-innies-and-outies.param.json',
 'killersudoku_killersudoku_12_3-4-innies-and-outies.param.json',
 'killersudoku_killersudoku_1_killersudoku.param.json',
 'killersudoku_killersudoku_2_extremekillersudokuwiki.param.json',
 'killersudoku_killersudoku_3_8-1-cage-unit-overlap.param.json',
 'killersudoku_killersudoku_4_1-1-innies-and-outies.param.json',
 'killersudoku_killersudoku_5_2-3-innies-and-outies.param.json',
 'killersudoku_killersudoku_6_4-5-innies-and-outies.param.json',
 'killersudoku_killersudoku_7_9-2-cage-unit-overlap.param.json',
 'killersudoku_killersudoku_8_10-3-cage-unit-overlap.param.json',
 'killersudoku_killersudoku_9_7-1-cage-splitting.param.json',
 'miracle_miracle_0_original.param.json',
 'skyscrapers_skyscrapers_16_2-high-numbers.param.json',
 'sudoku_sudokuwiki_0_hiddenpairs-2.param.json',
 'sudoku_sudokuwiki_10_perfect333swordfish.param.json',
 'sudoku_sudokuwiki_11_swordfish-2.param.json',
 'sudoku_sudokuwiki_12_skloops-3.param.json',
 'sudoku_sudokuwiki_13_skloops-1.param.json',
 'sudoku_sudokuwiki_14_skloops-2.param.json',
 'sudoku_sudokuwiki_15_3dmedusa-8.param.json',
 'sudoku_sudokuwiki_16_3dmedusa-9.param.json',
 'sudoku_sudokuwiki_17_3dmedusa-7.param.json',
 'sudoku_sudokuwiki_18_3dmedusa-5.param.json',
 'sudoku_sudokuwiki_19_3dmedusa-1.param.json',
 'sudoku_sudokuwiki_1_hiddentriples.param.json',
 'sudoku_sudokuwiki_20_3dmedusa-3.param.json',
 'sudoku_sudokuwiki_21_3dmedusa-4.param.json',
 'sudoku_sudokuwiki_22_3dmedusa-6.param.json',
 'sudoku_sudokuwiki_23_3dmedusa-2.param.json',
 'sudoku_sudokuwiki_24_hiddensingles.param.json',
 'sudoku_sudokuwiki_25_BUG-2.param.json',
 'sudoku_sudokuwiki_26_BUG-1.param.json',
 'sudoku_sudokuwiki_27_extuniqrectangles-2.param.json',
 'sudoku_sudokuwiki_28_extuniqrectangles-1.param.json',
 'sudoku_sudokuwiki_29_extuniqrectangles-3.param.json',
 'sudoku_sudokuwiki_2_hiddenpairs-1.param.json',
 'sudoku_sudokuwiki_30_hiddenuniqrectangles-2.param.json',
 'sudoku_sudokuwiki_31_hiddenuniqrectangles-4.param.json',
 'sudoku_sudokuwiki_32_hiddenuniqrectangles-3.param.json',
 'sudoku_sudokuwiki_33_hiddenuniqrectangles-1.param.json',
 'sudoku_sudokuwiki_34_jellyfish-3.param.json',
 'sudoku_sudokuwiki_35_jellyfish-1.param.json',
 'sudoku_sudokuwiki_36_jellyfish-4.param.json',
 'sudoku_sudokuwiki_37_jellyfish-2.param.json',
 'sudoku_sudokuwiki_38_nakedtriples-2.param.json',
 'sudoku_sudokuwiki_39_nakedpairs-1.param.json',
 'sudoku_sudokuwiki_3_xychain-2.param.json',
 'sudoku_sudokuwiki_40_nakedtriples-1.param.json',
 'sudoku_sudokuwiki_41_nakedpairs-2.param.json',
 'sudoku_sudokuwiki_42_ywing.param.json',
 'sudoku_sudokuwiki_43_xwing-2.param.json',
 'sudoku_sudokuwiki_44_xwing-1.param.json',
 'sudoku_sudokuwiki_45_xcycles.param.json',
 'sudoku_sudokuwiki_46_tripleblr.param.json',
 'sudoku_sudokuwiki_47_boxlinereduction.param.json',
 'sudoku_sudokuwiki_48_singlechains-1.param.json',
 'sudoku_sudokuwiki_49_simplecolouring-2.param.json',
 'sudoku_sudokuwiki_4_xychain-1.param.json',
 'sudoku_sudokuwiki_50_singlechains-4.param.json',
 'sudoku_sudokuwiki_51_hiddenquads-2.param.json',
 'sudoku_sudokuwiki_52_hiddenquads-1.param.json',
 'sudoku_sudokuwiki_53_nakedquads.param.json',
 'sudoku_sudokuwiki_54_pointingpairs-1.param.json',
 'sudoku_sudokuwiki_55_pointingpairs-2.param.json',
 'sudoku_sudokuwiki_56_pointingtriples.param.json',
 'sudoku_sudokuwiki_57_uniquerectangles-8.param.json',
 'sudoku_sudokuwiki_58_uniquerectangles-10.param.json',
 'sudoku_sudokuwiki_59_uniquerectangles-11.param.json',
 'sudoku_sudokuwiki_5_wxyzwing-4.param.json',
 'sudoku_sudokuwiki_60_uniquerectangles-9.param.json',
 'sudoku_sudokuwiki_61_uniquerectangles-1.param.json',
 'sudoku_sudokuwiki_62_uniquerectangles-3.param.json',
 'sudoku_sudokuwiki_63_uniquerectangles-7.param.json',
 'sudoku_sudokuwiki_64_uniquerectangles-5.param.json',
 'sudoku_sudokuwiki_65_uniquerectangles-2.param.json',
 'sudoku_sudokuwiki_66_uniquerectangles-4.param.json',
 'sudoku_sudokuwiki_67_uniquerectangles-6.param.json',
 'sudoku_sudokuwiki_68_alignedpairexclusion-3.param.json',
 'sudoku_sudokuwiki_69_alignedpairexclusion-1.param.json',
 'sudoku_sudokuwiki_6_wxyzwing-2.param.json',
 'sudoku_sudokuwiki_70_alignedpairexclusion-5.param.json',
 'sudoku_sudokuwiki_71_alignedpairexclusion-2.param.json',
 'sudoku_sudokuwiki_72_alignedpairexclusion-6.param.json',
 'sudoku_sudokuwiki_73_alignedpairexclusion-4.param.json',
 'sudoku_sudokuwiki_74_xyzwing-1.param.json',
 'sudoku_sudokuwiki_75_xyzwing-2.param.json',
 'sudoku_sudokuwiki_7_wxyzwing-1.param.json',
 'sudoku_sudokuwiki_8_wxyzwing-3.param.json',
 'sudoku_sudokuwiki_9_swordfish-1.param.json',
 'tents_tents_1_tectonic-9.param.json',
 'tents_tents_2_tents-1.param.json',
 'tents_tents_3_tectonic-1-2-3-4-5-6-7.param.json',
 'x-sums_x-sums_0_ctc-best-xsums.param.json']

demystify_instances = [
    puzzle for puzzle in demystify_puzzles() if not puzzle.startswith("sudoku") and puzzle in explained_demystify_instances
]


# print([p for p in demystify_puzzles() if 'sudoku' in p])
all_params_RQ2c_DEMYSTIFY_PUZZLES = rq2_not_incremental(
    output_folder=RQ2c_DEMYSTIFY_PUZZLES_HPC_OUTPUT_FOLDER,
    selected_instances=demystify_instances
)


all_params_to_sbatch_files(
    all_params=all_params_RQ2c_DEMYSTIFY_PUZZLES,
    base_fname=base_fname_RQ2c_DEMYSTIFY_PUZZLES,
    input_folder=RQ2c_DEMYSTIFY_PUZZLES_LOCAL_INPUT_FOLDER,
    output_folder=RQ2c_DEMYSTIFY_PUZZLES_HPC_OUTPUT_FOLDER
)

ini_folder(RQ2c_DEMYSTIFY_PUZZLES_LOCAL_OUTPUT_FOLDER)

print(f"{len(all_params_RQ2c_DEMYSTIFY_PUZZLES)=}")


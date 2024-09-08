from pathlib import Path
from pyexplain.benchmark.generate_params import HOURS, all_sudokus, rq2_selected_config
from pyexplain.examples.utils import DIFFICULTY_FNAME
from datetime import datetime
from pyexplain.solvers.params import BestStepParams, COusNonIncrParams, COusParams, ExplanationComputer, Grow, Interpretation, Weighing
from pyexplain.examples.frietkot import *

instance_no_timeout = ['binairo_binairo_100_40.param.json',
 'binairo_binairo_101_34.param.json', 'binairo_binairo_102_10.param.json', 'binairo_binairo_103_12.param.json', 'binairo_binairo_104_36.param.json', 'binairo_binairo_105_32.param.json', 'binairo_binairo_106_16.param.json', 'binairo_binairo_107_8.param.json', 'binairo_binairo_108_14.param.json', 'binairo_binairo_109_29.param.json', 'binairo_binairo_10_48.param.json', 'binairo_binairo_110_48.param.json', 'binairo_binairo_111_30.param.json', 'binairo_binairo_112_13.param.json', 'binairo_binairo_113_37.param.json', 'binairo_binairo_114_35.param.json', 'binairo_binairo_115_11.param.json', 'binairo_binairo_116_28.param.json', 'binairo_binairo_117_50.param.json', 'binairo_binairo_118_15.param.json', 'binairo_binairo_119_31.param.json', 'binairo_binairo_11_30.param.json', 'binairo_binairo_120_49.param.json', 'binairo_binairo_121_33.param.json', 'binairo_binairo_122_9.param.json', 'binairo_binairo_123_17.param.json', 'binairo_binairo_124_26.param.json', 'binairo_binairo_125_5.param.json', 'binairo_binairo_126_47.param.json',
 'binairo_binairo_127_45.param.json', 'binairo_binairo_128_7.param.json', 'binairo_binairo_129_19.param.json', 'binairo_binairo_12_13.param.json', 'binairo_binairo_130_24.param.json', 'binairo_binairo_131_3.param.json', 'binairo_binairo_132_20.param.json', 'binairo_binairo_133_41.param.json', 'binairo_binairo_134_39.param.json', 'binairo_binairo_135_43.param.json', 'binairo_binairo_136_22.param.json', 'binairo_binairo_137_1.param.json', 'binairo_binairo_138_44.param.json', 'binairo_binairo_139_25.param.json', 'binairo_binairo_13_37.param.json', 'binairo_binairo_140_18.param.json', 'binairo_binairo_141_6.param.json', 'binairo_binairo_142_4.param.json', 'binairo_binairo_143_27.param.json', 'binairo_binairo_144_46.param.json', 'binairo_binairo_145_42.param.json', 'binairo_binairo_146_23.param.json', 'binairo_binairo_147_21.param.json', 'binairo_binairo_148_2.param.json', 'binairo_binairo_149_38.param.json', 'binairo_binairo_14_35.param.json', 'binairo_binairo_150_40.param.json', 'binairo_binairo_151_7_Advanced_Technique_2.param.json',
 'binairo_binairo_152_5_Avoiding_Row_or_column_dup.param.json', 'binairo_binairo_154_6_Advanced_Technique_1.param.json', 'binairo_binairo_155_1_Avoiding_Triples_1.param.json', 'binairo_binairo_156_2_Avoiding_Triples_2.param.json', 'binairo_binairo_157_3_Avoiding_Triples_3.param.json', 'binairo_binairo_15_11.param.json', 'binairo_binairo_16_28.param.json', 'binairo_binairo_17_50.param.json', 'binairo_binairo_18_15.param.json', 'binairo_binairo_19_31.param.json', 'binairo_binairo_1_34.param.json', 'binairo_binairo_20_49.param.json', 'binairo_binairo_21_33.param.json', 'binairo_binairo_22_9.param.json', 'binairo_binairo_23_17.param.json', 'binairo_binairo_24_26.param.json', 'binairo_binairo_25_5.param.json', 'binairo_binairo_26_47.param.json', 'binairo_binairo_27_45.param.json', 'binairo_binairo_28_7.param.json', 'binairo_binairo_29_19.param.json', 'binairo_binairo_2_10.param.json', 'binairo_binairo_30_24.param.json', 'binairo_binairo_31_3.param.json', 'binairo_binairo_32_20.param.json', 'binairo_binairo_33_41.param.json', 'binairo_binairo_34_39.param.json', 'binairo_binairo_35_43.param.json', 'binairo_binairo_36_22.param.json', 'binairo_binairo_37_1.param.json', 'binairo_binairo_38_44.param.json', 'binairo_binairo_39_25.param.json', 'binairo_binairo_3_12.param.json', 'binairo_binairo_40_18.param.json', 'binairo_binairo_41_6.param.json', 'binairo_binairo_42_4.param.json', 'binairo_binairo_43_27.param.json', 'binairo_binairo_44_46.param.json', 'binairo_binairo_45_42.param.json', 'binairo_binairo_46_23.param.json', 'binairo_binairo_47_21.param.json', 'binairo_binairo_48_2.param.json', 'binairo_binairo_49_38.param.json', 'binairo_binairo_4_36.param.json', 'binairo_binairo_50_40.param.json', 'binairo_binairo_51_34.param.json', 'binairo_binairo_52_10.param.json', 'binairo_binairo_53_12.param.json', 'binairo_binairo_54_36.param.json', 'binairo_binairo_55_32.param.json', 'binairo_binairo_56_16.param.json', 'binairo_binairo_57_8.param.json', 'binairo_binairo_58_14.param.json', 'binairo_binairo_59_29.param.json', 'binairo_binairo_5_32.param.json', 'binairo_binairo_60_48.param.json', 'binairo_binairo_61_30.param.json', 'binairo_binairo_62_13.param.json', 'binairo_binairo_63_37.param.json', 'binairo_binairo_64_35.param.json', 'binairo_binairo_65_11.param.json', 'binairo_binairo_66_28.param.json', 'binairo_binairo_67_50.param.json', 'binairo_binairo_68_15.param.json', 'binairo_binairo_69_31.param.json', 'binairo_binairo_6_16.param.json', 'binairo_binairo_70_49.param.json', 'binairo_binairo_71_33.param.json', 'binairo_binairo_72_9.param.json', 'binairo_binairo_73_17.param.json', 'binairo_binairo_74_26.param.json', 'binairo_binairo_75_5.param.json', 'binairo_binairo_76_47.param.json', 'binairo_binairo_77_45.param.json', 'binairo_binairo_78_7.param.json', 'binairo_binairo_79_19.param.json', 'binairo_binairo_7_8.param.json', 'binairo_binairo_80_24.param.json', 'binairo_binairo_81_3.param.json', 'binairo_binairo_82_20.param.json', 'binairo_binairo_83_41.param.json', 'binairo_binairo_84_39.param.json', 'binairo_binairo_85_43.param.json', 'binairo_binairo_86_22.param.json', 'binairo_binairo_87_1.param.json', 'binairo_binairo_88_44.param.json', 'binairo_binairo_89_25.param.json', 'binairo_binairo_8_14.param.json', 'binairo_binairo_90_18.param.json', 'binairo_binairo_91_6.param.json', 'binairo_binairo_92_4.param.json', 'binairo_binairo_93_27.param.json', 'binairo_binairo_94_46.param.json', 'binairo_binairo_95_42.param.json', 'binairo_binairo_96_23.param.json', 'binairo_binairo_97_21.param.json', 'binairo_binairo_98_2.param.json', 'binairo_binairo_99_38.param.json', 'binairo_binairo_9_29.param.json', 'garam_garam_10_garam-diff-201120.param.json', 'garam_garam_11_garam-tut.param.json', 'garam_garam_1_garam-adv-201120.param.json', 'garam_garam_2_garam-master-201120.param.json', 'garam_garam_3_garam-beg-201120.param.json', 'garam_garam_4_garam-fiend-201120.param.json', 'garam_garam_5_garam-exp-201120.param.json', 'garam_garam_7_garam-easy-201120.param.json', 'garam_garam_8_garam-medium-201120.param.json', 'garam_garam_9_garam-vdiff-201120.param.json', 'kakurasu_kakurasu.param_0_kakurasu.param.json', 'kakuro_kakuro_0_conceptispuzzles.param.json', 'kakuro_kakuro_1_2-definitions-intersection.param.json', 'kakuro_kakuro_2_3-min-max-vals-sum-grp.param.json', 'kakuro_kakuro_3_1-row-col-restrictions.param.json', 'kakuro_kakuro_4_2-filled-areas.param.json', 'kakuro_kakuro_5_1-combo-ref.param.json', 'nonogram_nonogram-1.param_0_nonogram-1.param.json', 'origin-problem', 'origin_origin.param_0_origin.param.json', 'p12', 'p13', 'p16', 'p18', 'p19', 'p20', 'p25', 'p93', 'pastaPuzzle', 'pasta_pasta.param_0_pasta.param.json', 'skyscrapers_skyscrapers_0_brainbashers-walkthrough.param.json', 'skyscrapers_skyscrapers_10_8-second-highest-second-square.param.json', 'skyscrapers_skyscrapers_11_11-adv-tech-3.param.json', 'skyscrapers_skyscrapers_12_5-alldiff.param.json', 'skyscrapers_skyscrapers_13_10-adv-tech-2.param.json', 'skyscrapers_skyscrapers_14_14-adv-tech-6.param.json', 'skyscrapers_skyscrapers_1_12-adv-tech-4.param.json', 'skyscrapers_skyscrapers_2_4-unique-skyscraper-seq.param.json', 'skyscrapers_skyscrapers_3_13-adv-tech-5.param.json', 'skyscrapers_skyscrapers_4_7-lowest-skyscraper-adjacent.param.json', 'skyscrapers_skyscrapers_5_3-high-skyscrapers-no-2.param.json', 'skyscrapers_skyscrapers_6_2-high-skyscrapers-no-1.param.json', 'skyscrapers_skyscrapers_7_9-adv-tech-1.param.json', 'skyscrapers_skyscrapers_8_6-highest-skyscraper-in-far-opposite.param.json', 'skyscrapers_skyscrapers_9_1-clues-of-1-N.param.json', 'star-battle_starbattle_0_FATAtalkexample.param.json', 'star-battle_starbattle_2_krazydad-tutorial.param.json', 'star-battle_starbattle_4_tectonic-row-or-col-elimination.param.json', 'star-battle_starbattle_5_logicmastersindia-example.param.json', 'sudoku-easy_0.json', 'sudoku-easy_1.json', 'sudoku-easy_10.json', 'sudoku-easy_11.json', 'sudoku-easy_12.json', 'sudoku-easy_13.json', 'sudoku-easy_14.json', 'sudoku-easy_15.json', 'sudoku-easy_16.json', 'sudoku-easy_17.json', 'sudoku-easy_18.json', 'sudoku-easy_19.json', 'sudoku-easy_2.json', 'sudoku-easy_20.json', 'sudoku-easy_21.json', 'sudoku-easy_22.json', 'sudoku-easy_23.json', 'sudoku-easy_24.json', 'sudoku-easy_3.json', 'sudoku-easy_4.json', 'sudoku-easy_5.json', 'sudoku-easy_6.json', 'sudoku-easy_7.json', 'sudoku-easy_8.json', 'sudoku-easy_9.json', 'sudoku-expert_0.json', 'sudoku-expert_1.json', 'sudoku-expert_10.json', 'sudoku-expert_11.json', 'sudoku-expert_12.json', 'sudoku-expert_13.json', 'sudoku-expert_14.json', 'sudoku-expert_15.json', 'sudoku-expert_16.json', 'sudoku-expert_17.json', 'sudoku-expert_18.json', 'sudoku-expert_19.json', 'sudoku-expert_2.json', 'sudoku-expert_20.json', 'sudoku-expert_21.json', 'sudoku-expert_22.json', 'sudoku-expert_23.json', 'sudoku-expert_24.json', 'sudoku-expert_3.json', 'sudoku-expert_4.json', 'sudoku-expert_5.json', 'sudoku-expert_6.json', 'sudoku-expert_7.json', 'sudoku-expert_8.json', 'sudoku-expert_9.json', 'sudoku-intermediate_0.json', 'sudoku-intermediate_1.json', 'sudoku-intermediate_10.json', 'sudoku-intermediate_11.json', 'sudoku-intermediate_12.json', 'sudoku-intermediate_13.json', 'sudoku-intermediate_14.json', 'sudoku-intermediate_15.json', 'sudoku-intermediate_16.json', 'sudoku-intermediate_17.json', 'sudoku-intermediate_18.json', 'sudoku-intermediate_19.json', 'sudoku-intermediate_2.json', 'sudoku-intermediate_20.json', 'sudoku-intermediate_21.json', 'sudoku-intermediate_22.json', 'sudoku-intermediate_23.json', 'sudoku-intermediate_24.json', 'sudoku-intermediate_3.json', 'sudoku-intermediate_4.json', 'sudoku-intermediate_5.json', 'sudoku-intermediate_6.json', 'sudoku-intermediate_7.json', 'sudoku-intermediate_8.json', 'sudoku-intermediate_9.json', 'sudoku-simple_0.json', 'sudoku-simple_1.json', 'sudoku-simple_10.json', 'sudoku-simple_11.json', 'sudoku-simple_12.json', 'sudoku-simple_13.json', 'sudoku-simple_14.json', 'sudoku-simple_15.json', 'sudoku-simple_16.json', 'sudoku-simple_17.json', 'sudoku-simple_18.json', 'sudoku-simple_19.json', 'sudoku-simple_2.json', 'sudoku-simple_20.json', 'sudoku-simple_21.json', 'sudoku-simple_22.json', 'sudoku-simple_23.json', 'sudoku-simple_24.json', 'sudoku-simple_3.json', 'sudoku-simple_4.json', 'sudoku-simple_5.json', 'sudoku-simple_6.json', 'sudoku-simple_7.json', 'sudoku-simple_8.json', 'sudoku-simple_9.json', 'tents_tents_0_tectonic-8.param.json', 'tents_tents_1_tectonic-9.param.json', 'tents_tents_2_tents-1.param.json', 'tents_tents_3_tectonic-1-2-3-4-5-6-7.param.json', 'thermometer_thermometer_0_1-some-tips.param.json']

def ini_folder(folder):
    # making sure the folder is available on the HPC
    with Path(folder + "ini.txt") as p:
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open("w+") as fp:
            fp.write(".")


def all_params_to_sbatch_files(all_params, base_fname, input_folder, output_folder, test_file=None):
    modulo = 1000

    if not Path(input_folder).exists():
        Path(input_folder).mkdir(parents=True)

    test_script = ["#!/bin/bash -l", ""]

    for script_id in range(len(all_params)//modulo+1):
        bash_file = Path(input_folder) / (base_fname + "run_experiments" + str(script_id)+".sh")

        script = ["#!/bin/bash -l", ""]

        for id, param in enumerate(all_params[script_id*modulo:(script_id+1)*modulo]):
            pbs_fname = base_fname + "_job_" + str(script_id*modulo+id) + ".sbatch"
            param.output = output_folder + base_fname + \
                "_results_" + str(script_id*modulo+id) + ".json"

            script.append(f"sbatch {pbs_fname}")

            test_params_joined = write_params_to_sbatch(input_folder, pbs_fname, param)

            if test_params_joined:
                test_script.append(test_params_joined)

        with bash_file.open('w+') as fp:
            fp.writelines(map(lambda x: x+"\n", script))

    if test_file is not None:
        with Path(test_file).open('w+') as fp:
            fp.writelines(map(lambda x: x+"\n", test_script))

def write_params_to_sbatch(output_folder: str, fname: str, params: BestStepParams):
    param_dict = params.to_dict()
    # print(param_dict)
    python_arguments = []

    python_arguments += ["python3 explanation_quality.py"]
    for k, v in param_dict.items():
        python_arguments.append(f"--{k}")
        if v is None or v == "":
            python_arguments.append(f"ignore")
        else:
            python_arguments.append(f"{v}")

    timeout = param_dict["timeout"]
    days = timeout // (3600 * 24)
    hours = (timeout - days * 24*3600) // 3600
    sec_value = (timeout - days * 24*3600) % 3600
    min_value = sec_value // 60
    sec_value %= 60

    PBS_script = f"""#!/bin/bash

#SBATCH --job-name={fname.replace(".pbs", "")}
#SBATCH --error=%x-%j.err
#SBATCH --out=%x-%j.out
#SBATCH --ntasks=1
#SBATCH --partition=skylake,skylake_mpi
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=emilio.gamba@vub.be
#SBATCH --time={days}-{hours}:{max([30, min_value])}:{sec_value}
#SBATCH --mem=16G

module purge
module load PySAT/0.1.7.dev1-GCC-10.2.0
module load SciPy-bundle/2020.11-foss-2020b
module load Gurobi/9.1.2-GCCcore-10.2.0

pydir="/data/brussel/101/vsc10143/OCUS_EXPLAIN/code"
export PYTHONPATH=${{VSC_DATA}}/cppy_src:${{PYTHONPATH}}
export PYTHONPATH=${{VSC_DATA}}/CPMpy/:${{PYTHONPATH}}
export PYTHONPATH=${{VSC_DATA}}/cpmpy/:${{PYTHONPATH}}

cd $pydir

{" ".join(python_arguments)}
"""
    p = Path(output_folder) / fname

    with p.open('w+') as fp:
        fp.write(PBS_script)

    if "4x4" in params.instance and params.explanation_computer is ExplanationComputer.MUS:
        return " ".join(python_arguments)

    return None


def generate_params():
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

    EXPLANATION_QUALITY_2 = "EXPLANATION_QUALITY_2/" + CURRENT_HOUR

    EXPLANATION_QUALITY_2_LOCAL_OUTPUT_FOLDER = LOCAL_OUTPUT + EXPLANATION_QUALITY_2
    EXPLANATION_QUALITY_2_HPC_OUTPUT_FOLDER = HPC_OUTPUT + EXPLANATION_QUALITY_2

    EXPLANATION_QUALITY_2_LOCAL_INPUT_FOLDER = LOCAL_INPUT + EXPLANATION_QUALITY_2
    EXPLANATION_QUALITY_2_HPC_INPUT_FOLDER = HPC_INPUT + EXPLANATION_QUALITY_2


    def ini_folder(folder):
        # making sure the folder is available on the HPC
        with Path(folder + "ini.txt") as p:
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
            with p.open("w+") as fp:
                fp.write(".")

    base_fname_EXPLANATION_QUALITY_2 = "EXPLANATION_QUALITY_2_"


    OCUS_INCREMENTAL_greedy_corr = rq2_selected_config(
        grow=Grow.CORR_GREEDY,
        interpretation=Interpretation.ACTUAL,
        weighing=Weighing.UNIFORM,
        output_folder=EXPLANATION_QUALITY_2_HPC_OUTPUT_FOLDER,
        param=COusParams,
        timeout=2 * HOURS,
        selected_instances=instance_no_timeout
    )

    all_params_to_sbatch_files(
        all_params=OCUS_INCREMENTAL_greedy_corr,
        base_fname=base_fname_EXPLANATION_QUALITY_2,
        input_folder=EXPLANATION_QUALITY_2_LOCAL_INPUT_FOLDER,
        output_folder=EXPLANATION_QUALITY_2_HPC_OUTPUT_FOLDER
    )

    print(f"{len(OCUS_INCREMENTAL_greedy_corr)=}")
    ini_folder(EXPLANATION_QUALITY_2_LOCAL_OUTPUT_FOLDER)

if __name__ == "__main__":
    generate_params()

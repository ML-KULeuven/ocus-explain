import json
from solvers.parameters import SMUSParams, MCS,  Assumptions, Grow
from solvers.solver import SMUS
from examples.examples import example_bacchus, example_smus
from pysat.formula import CNF
from pysat.solvers import Solver
from pathlib import Path
from datetime import datetime
import subprocess
import time

INPUT_FOLDER = 'benchmark/data/input/'
OUTPUT_FOLDER = 'benchmark/data/output/'
EASY_INSTANCES_FOLDER = INPUT_FOLDER + 'easy/'
MEDIUM_INSTANCES_FOLDER = INPUT_FOLDER + 'medium/'
HARD_INSTANCES_FOLDER = INPUT_FOLDER + 'hard/'


def all_smus_params():
    all_params = []
    for assumption in list(Assumptions):
        for grow in list(Grow):
            for mcses in list(MCS):
                params = SMUSParams()
                params.assumptions = assumption
                params.grow = grow
                params.mcses = mcses
                all_params.append(params)
    return all_params

def save_cnfs():
    smus_cnf = example_smus()
    bacchus_cnf = example_bacchus()
    # params = SMUSParams()
    # smus = SMUS(from_cnf=cnf, params=params)
    # smus.compute()

    with open(EASY_INSTANCES_FOLDER + 'smus.cnf', 'w+') as fp:
        smus_cnf.to_fp(fp)  # writing to the file pointer
    with open(EASY_INSTANCES_FOLDER + 'bacchus.cnf', 'w+') as fp:
        bacchus_cnf.to_fp(fp)  # writing to the file pointer

def extract_cnf_from_folder(folder):
    path_folder = Path(folder)
    instances = []
    for elem in path_folder.iterdir():
        if elem.is_dir():
            instances += extract_cnf_from_folder(elem)
        elif elem.is_file() and elem.suffix == ".cnf":
            instances.append(elem)

    return instances

def repair_instance(instance):
    p = Path(instance)
    symbols = "!@#$%^&*()_+={}[]"
    print(instance)
    with p.open('r') as fp:
        lines = []
        all_lines = fp.readlines()
        for line in all_lines:
            if line.startswith('c') or line.startswith('p'):
                lines.append(line)
            elif len(line) == 0 or line =="\n":
                continue
            elif line == "0\\n" or any(True if symbol in line else False for symbol in symbols):
                continue
            else:
                lines.append(line)
        print(all_lines)
    with p.open('w+') as fp:
        fp.writelines(lines)

def check_cnf_from_folder(folder):
    # sort instances by difficulty
    instances = [str(f) for f in extract_cnf_from_folder(folder)]
    # for instance in instances:
    #     repair_instance(instance)
    for instance in instances:
        with Solver(bootstrap_with=CNF(from_file = instance)) as s:
            assert s.solve() == False

    return instances

def easy_instances():
    instances = check_cnf_from_folder(EASY_INSTANCES_FOLDER)
    instances.sort(key=lambda l: CNF(from_file=l).nv)
    return instances

def medium_instances():
    instances = check_cnf_from_folder(MEDIUM_INSTANCES_FOLDER)
    instances.sort(key=lambda l: CNF(from_file=l).nv)
    return instances

def hard_instances():
    instances = check_cnf_from_folder(HARD_INSTANCES_FOLDER)
    instances.sort(key=lambda l: CNF(from_file=l).nv)
    return instances

def json_write(results, output):
    with Path(output).open('w+') as f:
        json.dump(results, f)

def smus_cnf(cnf, params, output):
    # capturing preperation time
    tprep = time.time()
    s = SMUS(from_file=cnf, params=params)
    tprep = time.time() - tprep

    # capturing solving time
    tsolv = time.time()
    hs = s.compute()
    tsolv = time.time() - tsolv

    # exporting results and params
    results = s.stats.to_dict()
    results.update(params.to_dict())
    results["solv_time"] = tsolv
    results["smus"] = list(hs)
    results["prep_time"] = tprep
    results["instance"] = Path(cnf).name.replace('.cnf', '')

    # write to json file
    json_write(results, output)

def minUC_output_to_dict(splitted_output):
    results = {}
    results["solver"] ="minUC"
    results["solved"] = True if 'c SOLVED' in splitted_output else False

    results["prep_time"] = [float(l.replace('c prepr. time: ', '')) for l in splitted_output if l.startswith('c prepr. time: ')][0]
    results["solv_time"] =[float(l.replace('c solv.  time: ', '')) for l in splitted_output if l.startswith('c solv.  time: ')][0]
    results["smus"] = [[int(cli) for cli in l.replace('v ','').replace(' 0','').split(' ')] for l in splitted_output if l.startswith('v ')][0]
    results["n_disj_MCSes"] = [int(l.replace('c disj MCSes: ', "")) for l in splitted_output if l.startswith('c disj MCSes: ')][0]
    results["n_unit_MCSes"] = [int(l.replace('c unit MCSes: ', "")) for l in splitted_output if l.startswith('c unit MCSes: ')][0]
    results["disj_MCSes"] = [l.replace("c MCS: ", "").replace(' 0','').split(' ') for l in splitted_output  if l.startswith("c MCS: ")]
    results["n_hs"] =  [int(l.replace('c iters total: ', "")) for l in splitted_output if l.startswith('c iters total: ')][0]
    results["refns"] =  [int(l.replace('c refns total: ', "")) for l in splitted_output if l.startswith('c refns total: ')][0] 
    return results

def minUC_cnf(cnf, output_file):
    assert type(cnf) is str and Path(cnf).exists(), f"invalid input:\n\t file={cnf}"
    # executing the smus algorithm on given cnf instance
    path_to_exec = "benchmark/minuc-linux-x86-64"
    arguments = ["-vv"]
    output = subprocess.run([path_to_exec] + arguments + [cnf], capture_output=True)
    splitted_output = output.stdout.decode('utf8').splitlines()
    results = minUC_output_to_dict(splitted_output)
    results["instance"] = Path(cnf).name.replace('.cnf', '')

    # write to json file
    json_write(results, output_file)

def test_unsat_instances(n=100):
    today = datetime.now().strftime("%Y%m%d%H")
    output_folder = Path(OUTPUT_FOLDER) / today
    if not output_folder.exists():
        output_folder.mkdir()

    instances = easy_instances()

    for id, instance in enumerate(instances):
        print(f"{id+1}/{len(instances)}")
        # run minUC solver
        instance_output = Path(instance).name.replace('.cnf', '')
        minuc_output = output_folder / ("minuc_" + instance_output + ".json")

        minUC_cnf(instance, minuc_output)

        # run SMUS solver
        for id, params in enumerate(all_smus_params()):
            smus_output = output_folder / ("smus_" + instance_output + f"_{id}.json")
            smus_cnf(instance, params, smus_output)

test_unsat_instances()

# smus_cnf = example_smus()
# bacchus_cnf = example_bacchus()
# params = SMUSParams()
# smus = SMUS(from_cnf=cnf, params=params)
# smus.compute()

# with open(EASY_INSTANCES_FOLDER + 'smus.cnf', 'w+') as fp:
#     smus_cnf.to_fp(fp)  # writing to the file pointer
# with open(EASY_INSTANCES_FOLDER + 'bacchus.cnf', 'w+') as fp:
#     bacchus_cnf.to_fp(fp)  # writing to the file pointer
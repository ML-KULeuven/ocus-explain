from pathlib import Path
import csv, json, random
import numpy as np
# CPPY modeling environment
from cppy import *
from cppy.model_tools.to_cnf import *
from pyexplain.examples.frietkot import *
# from sudoku_cpmpy import model_sudoku_cpmpy

NROWS       = 9
NCOLS       = 9
NVALUES     = 9
NBOXROWS    = 3
NBOXCOLS    = 3

DIFFICULTY_FNAME = {
    '4x4'           : 'pyexplain/examples/sudoku/4_4_sudokus.csv',
    'simple'        : 'pyexplain/examples/sudoku/simple_sudokus.csv',
    'easy'          : 'pyexplain/examples/sudoku/easy_sudokus.csv',
    'intermediate'  : 'pyexplain/examples/sudoku/intermediate_sudokus.csv',
    'expert'        : 'pyexplain/examples/sudoku/expert_sudokus.csv',
    '16x16'         : 'pyexplain/examples/sudoku/16x16.csv',
    '25x25'         : 'pyexplain/examples/sudoku/25x25.csv',
}

DEMISTIFY_FOLDER = "pyexplain/examples/demistify/pickles/"
DEMISTIFY_MULTIPLE_SOLUTIONS_FOLDER = "pyexplain/examples/demistify/pickles-multiple-solutions/"

def flat(ll):
    return [e for l in ll for e in l]

def sudoku_str_to_numpy_array(sudoku_str: str):

    cleaned_str = sudoku_str.replace('\n', '').strip()

    ## new data!
    if ' ' in cleaned_str:
        splitted_cleaned_str = cleaned_str.split(' ')

        n = int(len(splitted_cleaned_str)**(1/2))
        return np.array(
            [[int(splitted_cleaned_str[i + j*n]) for i in range(n)] for j in range(n)]
        )
    ## old data !
    else:
        n = int(len(cleaned_str)**(1/2))
        return np.array(
            [[int(cleaned_str[i + j*n]) for i in range(n)] for j in range(n)]
        )

def get_sudoku_grid(instance: str):
    _, difficulty, offset = instance.split('-')
    fname = DIFFICULTY_FNAME[difficulty]
    sudoku_grid = None

    with open(fname) as csvfile:
        cnt = 0
        for  row in csv.DictReader(csvfile):

            if int(row['Solution Count']) != 1:
                continue

            if cnt != int(offset):
                cnt += 1
                continue

            sudoku_grid = sudoku_str_to_numpy_array(row['Puzzle'])

    n = len(sudoku_grid)
    assert all(len(row) == n for row in sudoku_grid), "All dimnesions must match!"
    return sudoku_grid

def csv_to_numpy_grids(fname, difficulty=None):
    sudoku_grids = []
    with open(fname) as csvfile:
        for row in csv.DictReader(csvfile):
            sudoku_grid = {
                'puzzle': sudoku_str_to_numpy_array(row['Puzzle']),
                'solution':  sudoku_str_to_numpy_array(row['Solution']) if 'Solution' in row else None,
            }
            if difficulty is not None:
                sudoku_grid['difficulty'] = difficulty
            # Checking for solution correctness
            sudoku_grids.append(sudoku_grid)

    return sudoku_grids

def get_random_sudoku_grid(difficulty='easy'):

    all_grids = csv_to_numpy_grids(DIFFICULTY_FNAME[difficulty], 'difficulty')

    return all_grids[random.randrange(len(all_grids))]

def all_sudoku_puzzles():
    all_grids = []
    for difficulty, fname in DIFFICULTY_FNAME.items():
        all_grids += csv_to_numpy_grids(fname, difficulty)

    return all_grids

def from_json_pickle(filename):
    with Path(filename).open() as fp:
        data = json.load(fp)
        problem_name  = data["name"] 
        param_name  = data["param_name"]
        cnf  = data["cnf"]
        assumptions = data["assumption"]
        user_vars = data["user_vars"]
        weights = {int(k): int(v) for k,v in data["weights"].items()}
    return problem_name, param_name, cnf, assumptions, user_vars, weights

def new_puzzle_data():
    return {
        # puzzle type: SUokdu, Logic, Demystify
        'puzzle_type':[],
        # type of puzzle: (4x4, 9x9, ..., origin, binairo, ...)
        'instance_type':[],
        'instance':[],
        # number of cnf clauses
        'cnf':[],
        # number of lits to explain
        'lits_to_explain':[],
        # number of instances of that type --> summarized in table :-)
        'n_instances': [],
        # number of clauses where [-lit, lit] are present
        'n_bij': [],
        # number of unit -clauses
        'n_units': [],
        # nu of unit -clauses that intersect with bijectivity clauses
        'n_units_to_check': []
    }

def sudoku_instances_data(base_path="", ignored_difficulties=["16x16", "25x25", "4x4"], selected_instances=None):

    instance_type_map = {
        '4x4' : '4x4', 
        'simple': '9x9',
        'intermediate': '9x9',
        'easy': '9x9',
        'expert': '9x9',
        '16x16': '16x16',
        '25x25':'25x25'
    }

    puzzle_data = new_puzzle_data()
    sudoku_pickles = [instance for instance in Path(base_path + "sudoku/pickles/").iterdir() if instance.suffix == ".json"]
    for id, instance in enumerate(sudoku_pickles):

        instance_file = instance.name
        if selected_instances is not None and  instance_file not in selected_instances:
            continue

        if any(diff in instance_file for diff in ignored_difficulties):
            continue

        instance_type = instance.name.replace('sudoku-', '').split('_')[0]

        print(f'{instance_type},\t{instance_file=}\t{id+1}/{len(sudoku_pickles)}', flush=True, end='\r')
        with open(instance, 'r') as file:
            data = json.load(file)

        p_clauses = data["cnf"]
        U = data["user_vars"]
        I = data["assumption"]

        u_abs = set(abs(l) for l in U)
        i_abs = set(abs(l) for l in I)
        n_lits_to_explain = len(u_abs - i_abs)
        n_cnf_clauses = len(p_clauses)
        n_bij, n_units, n_units_to_check = 0, 0, 0
        puzzle_data["puzzle_type"].append('sudoku')
        puzzle_data['instance_type'].append(instance_type_map[instance_type] + "-" + instance_type)
        puzzle_data['instance'].append(instance_file)
        puzzle_data['cnf'].append(n_cnf_clauses)
        puzzle_data['lits_to_explain'].append(n_lits_to_explain)
        puzzle_data['n_instances'].append(1)
        puzzle_data['n_bij'].append(n_bij)
        puzzle_data['n_units'].append(n_units)
        puzzle_data['n_units_to_check'].append(n_units_to_check)

    return puzzle_data

def logic_puzzles_data():
    puzzle_data = new_puzzle_data()
    puzzle_funs = {
        "origin-problem": originProblem,
        "pastaPuzzle": pastaPuzzle,
        "p12": p12,
        "p13": p13,
        "p16": p16,
        "p18": p18,
        "p25": p25,
        "p20": p20,
        "p93": p93,
        "p19": p19
    }
    for puzzle, puzzle_fun in puzzle_funs.items():
        p_clauses, p_ass, p_weights, p_user_vars, matching_table = puzzle_fun()
        # User vocabulary
        U = p_user_vars | set(x for lst in p_ass for x in lst)
        I = set(x for lst in p_ass for x in lst)
        u_set = set(abs(l) for l in U)
        i_set = set(abs(l) for l in I)
        n_bij, n_units, n_units_to_check = bijectivity_check(p_clauses)

        puzzle_data["puzzle_type"].append('logic')
        
        puzzle_data['instance'].append(puzzle)
        puzzle_data['cnf'].append(len(p_clauses))
        puzzle_data['lits_to_explain'].append(len(u_set-i_set))
        puzzle_data['instance_type'].append(len(u_set-i_set))
        puzzle_data['n_instances'].append(1)
        puzzle_data['n_bij'].append(n_bij)
        puzzle_data['n_units'].append(n_units)
        puzzle_data['n_units_to_check'].append(n_units_to_check)
    return puzzle_data

def bijectivity_check(clauses, verbose=False):
    n_tot = len(clauses)
    n_bij = 0
    lits_to_check = set()
    units = set()
    for clause in clauses:
        cleaned_clause = set(abs(l) for l in clause)
        if len(clause) == 1:
            units |= cleaned_clause
        elif len(clause) == 2 and len(cleaned_clause) == 1:
            n_bij += 1
            lits_to_check |= cleaned_clause
    if verbose:
        print(f"\n\t->%bij = {round(n_bij/n_tot*100, 2)}")
        # n_units = 0
        # for id, lit in enumerate(lits_to_check):
        #     print(f"{id+1}/{len(lits_to_check)}", flush=True, end='\r')
        #     if -lit in units or [lit] in units:
        #         n_units += 1
        print(f"\t->%units = {round(len(units)/n_tot*100, 2)}")

        # print(f"\t->%units propagatable = {round(n_units/n_tot*100)} - {round(n_units/len(units)*100)}")
        if len(units) > 0:
            print(f"\t->%units propagatable = {round(len(units & lits_to_check)/n_tot*100, 2)} - {round(len(units & lits_to_check)/len(units)*100, 2)} [{len(units & lits_to_check)}/{n_tot}]\n")
    return n_bij, len(units), len(units & lits_to_check)

def demystify_instances_data(base_path="", selected_instances=None):
    puzzle_data = new_puzzle_data()
    demystify_pickles = base_path + 'demistify/pickles/'
    for pickle in Path(demystify_pickles).iterdir():
        
        if pickle.suffix == '.json':
            if selected_instances is not None and pickle.name not in selected_instances:
                continue
            with pickle.open('r') as f:
                data = json.load(f)
                print(pickle.name, "\t->\t", pickle.name.split('_')[0])
                n_bij, n_units, n_units_to_check = bijectivity_check(data["cnf"])
                puzzle_data["puzzle_type"].append('demystify')
                puzzle_data['instance_type'].append(pickle.name.split('_')[0])
                puzzle_data['instance'].append(pickle.name)
                puzzle_data['cnf'].append(len(data['cnf']))
                puzzle_data['lits_to_explain'].append(len(data["user_vars"]))
                puzzle_data['n_instances'].append(1)
                puzzle_data['n_bij'].append(n_bij)
                puzzle_data['n_units'].append(n_units)
                puzzle_data['n_units_to_check'].append(n_units_to_check)
    return puzzle_data

def combine_data(*all_puzzle_data):
    empty_data = new_puzzle_data()
    for puzzle_data in all_puzzle_data:
        for k in empty_data.keys():
            empty_data[k] += puzzle_data[k]
    return empty_data

def export_data(data, filename):
    with Path(filename).open('w') as f:
        json.dump(data, f)

def get_easiest_instances_demystify():
    instances = []
    added_puzzles = []
    pickles = [pickle for pickle in Path('demistify/pickles/').iterdir() if pickle.is_file() and pickle.suffix == ".json"]
    sorted_pickles = sorted(pickles, key=lambda x: x.stat().st_size)

    for pickle in sorted_pickles:
        instance_type = pickle.name.split('_')[0]
        if instance_type not in added_puzzles:
            instances.append(pickle.name)
            added_puzzles.append(instance_type)

    with Path("demistify/sample_demystify_instances.json").open('w+') as fp:
        json.dump(instances, fp)
    return instances

def sudoku_from_json_pickle(instance):

    with Path(instance).open() as fp:
        data = json.load(fp)
        problem_name  = data["name"] 
        cnf  = data["cnf"]
        assumptions = data["assumption"]
        user_vars = data["user_vars"]
        weights = {int(k): int(v) for k,v in data["weights"].items()}
    return problem_name, cnf, user_vars, assumptions, weights

## Gen Table for all 
if __name__ == '__main__':
    easiest_demystify_instances = get_easiest_instances_demystify()
    
    # demystify_data = demystify_instances_data()
    # export_data(demystify_data, 'puzzle_info/demystify_data.json')

    # logic_data = logic_puzzles_data()
    # export_data(logic_data, 'puzzle_info/logic_data.json')

    # sudoku_data = sudoku_instances_data()
    # export_data(sudoku_data, 'puzzle_info/sudoku_info.json')

    # ## COMBINE DATA
    # all_instances_data = combine_data(sudoku_data, logic_data, demystify_data)
    # export_data(all_instances_data, 'puzzle_info/all_puzzles.json')
    # print(all_instances_data)
    ## df = pd.DataFrame.from_dict(all_instances_data)
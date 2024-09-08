#!/usr/bin/env python3
import json
from re import A
import warnings
import argparse
from pathlib import Path

from demystify import explain
from pyexplain.utils.utils import cost_puzzle
from pysat.solvers import Solver
from pysat.formula import CNF

PATH_HOME_CODE = "/Users/emiliogamba/Documents/GitHub/OCUSExplanations/code/"

def from_eprime(eprime, eprimeparam):
    """
        fromEprime: Takes a .eprime puzzle description and a .param puzzle instance
        and parses it using the Demystify tool. The relevant internals from the Demystify
        solver are then extracted for use by pyexplain.
    """
    exp = explain.Explainer()

    print("\t\t\tInit from essence")
    try:
        exp.init_from_essence(eprime, eprimeparam)
    except explain.SolveError as e:
        print(f"\n{e=}\n\t{eprime=}\n\t{eprimeparam=} does not have a unique solution.\n")

    p_clauses = exp.solver._cnf.clauses
    print("\t\t\tclauses", len(p_clauses))
    p_ass = [[c] for c in exp.solver._conlits]
    print("\t\t\tconflicts", len(p_ass))

    p_weights = {c:20 for c in exp.solver._conlits} # Demystify has no weighting so weight everything equally.
    print("\t\t\tweights", len(p_weights))
    p_user_vars = list(exp.solver._varsmt)
    print("\t\t\tp_user_vars", len(p_user_vars))

    return p_clauses, p_ass, p_weights, p_user_vars, None, exp

def convert_to_demystify_output(p_output, exp, outputfile):
    """
        convert_to_demystify_output: Takes the Demystify solver (exp) and the 
        dict produced by pyexplain (p_output) and creates a JSON file readable by the
        Demystify Visualiser.
    """
    output_dict = {"name": exp.name, "params": exp.params, "steps": []}

    for p_step in p_output:
        proven_lits = []
        for l in p_step["derived"]:
            if l > 0:
                proven_lits.append(exp.solver._varsmt2litmap[l][0])
            else:
                proven_lits.append(exp.solver._varsmt2neglitmap[-l][0])

        mus = [exp.solver._conmap[x] for x in p_step["constraints"] if x in exp.solver._conmap]
        output_dict["steps"].append(exp._get_step_dict(proven_lits, mus))
        exp._add_known(proven_lits)

    file = open(outputfile + "-demystify-out.json", "w")
    file.write(json.dumps(output_dict))
    file.close()

def pickle_demistify_puzzle(filename, problem_name, param_name, p_clauses, p_ass, p_weights, p_user_vars):

    puzzle_specification = {
        'name': problem_name,
        'param_name': param_name,
        'cnf': p_clauses,
        'assumption': p_ass,
        'user_vars': p_user_vars,
        'weights': p_weights
    }

    with open(filename, "w") as fp:
        json.dump(puzzle_specification, fp)

def unique_solution(p_clauses, p_ass, p_weights, p_user_vars):
    assumptions = [l for row in p_ass for l in row]
    assert len(assumptions) == len(set(assumptions)), "Ensure no duplicates produced by Essence prime."
    assert all(True if -l not in assumptions else False for l in assumptions), "Ensure not both polarities present in file"

    with Solver(bootstrap_with=p_clauses) as s:
        assert s.solve(), "Not solvable"
        assert s.solve(assumptions=assumptions), "Not solvable with given assumptions"

        for id, m in enumerate(s.enum_models(assumptions=assumptions)):
            if id > 0:
                return False
    return True

def get_all_params(dirname: Path):
    # create a list of file and sub directories 
    # names in the given directory
    if dirname.is_file():
        return [dirname]

    list_dirs = [f for f in dirname.iterdir() if f.is_dir()]
    list_params_files = [f for f in dirname.iterdir() if f.is_file() and f.suffix == ".param"]

    for d in list_dirs:
        list_params_files += get_all_params(d)
    return list_params_files

def pickle_all_demystify_puzzles(eprime_param_mapping, output_folder=None, ignored=[]):
    if output_folder is None:
        output_folder = 'pyexplain/examples/demistify/pickles/'

    for id, (problem, all_eprime_params) in enumerate(eprime_param_mapping.items()):
        if problem in ignored:
            print(f"{id}:\tAlready completed:\t{problem}")
            continue
        eprime = all_eprime_params["eprime"]
        params = all_eprime_params["params"]
        print(f"{id=}\t{problem=}\t{all_eprime_params=}")

        for eprimeparam in params:
            p = Path(eprimeparam)
            all_param_files = get_all_params(p)
            print(f"\n{p=} [{len(all_param_files)} files]")

            # iterate over dir and add all_puzzle_problems
            for id, f in enumerate(all_param_files):
                print(f"\t [{id+1}\t/{len(all_param_files)}]{f=}")

                filename = output_folder + f"{problem}_{p.name}_{id}_{f.name}.json"
                if Path(filename).exists():
                    continue

                try:
                    p_clauses, p_ass, p_weights, p_user_vars, _, _ = from_eprime(eprime, str(f))
                    unique_sol = unique_solution(p_clauses, p_ass, p_weights, p_user_vars)
                    if not unique_sol:
                        filename = 'pyexplain/examples/demistify/pickles-multiple-solutions/' + f"{problem}_{p.name}_{id}_{f.name}.json"
                except AssertionError as e:
                    ## cannot be solved with current assumptions
                    print(f"\n{e=}\n\t{problem=}\n\t{eprime=}\n\t{eprimeparam=} - {p=}\n\tparam_file={f=}")
                    continue
                except Exception as e:
                    print(f"\n{e=}\n\t{problem=}\n\t{eprime=}\n\t{eprimeparam=} - {p=}\n\tparam_file={f=}")
                    continue

                assert all(i is not None and len(i) > 0 for i in [p_clauses, p_ass, p_weights, p_user_vars]), "Ensure not empty problem"

                pickle_demistify_puzzle(filename, problem, f.name, p_clauses, p_ass, p_weights, p_user_vars)

def check_clauses_units(p_clauses, p_ass, p_weights, p_user_vars):
    elems_to_check, unit_clauses = [], []
    for id, clause in enumerate(p_clauses):
        if len(clause) == 1:
            elems_to_check.append((id, clause[0]))
        elif len(clause) == 0:
            warnings.warn(f"Empty clause {id} {clause}")

    for (elem_clause_id, lit) in elems_to_check:
        present = False
        for id, cl in enumerate(p_clauses):
            if elem_clause_id == id:
                continue
            if lit in cl or -lit in cl:
                present = True
                break

        if not present:
            unit_clauses.append(lit)

    return unit_clauses

def extract_problem_size(folder):
    p = Path(folder)
    print(f'problem\t\tinstance\t\t#clauses\t\t#literals explain')
    for pi in p.iterdir():
        if pi.is_file() and pi.suffix == ".json":
            with pi.open() as json_file:
                data = json.load(json_file)
                print(f'{data["name"]}\t\t{data["param_name"]}\t\t{len(data["cnf"])}\t\t{len(data["user_vars"])}')

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--eprime", help="Use demystify essence prime input: .eprime file")
    # parser.add_argument("--eprimeparam", help="Use demystify essence prime input: .param file")

    # args = parser.parse_args()

    # p_clauses, p_ass, p_weights, p_user_vars, matching_table, explainer = from_eprime(
    #     eprime=args.eprime,eprimeparam=args.eprimeparam
    # )
    # print(f"\n\t{p_clauses=}, \n\t {p_ass=},\n\t {p_weights=},\n\t {p_user_vars=}")
    # unit_clauses = check_clauses_units(p_clauses, p_ass, p_weights, p_user_vars)

    # print(get_all_params(Path("pyexplain/examples/demistify/problems/binairo")))
    encoded_puzzles = [
        "killersudoku"
    ]
    with open('pyexplain/examples/demistify/puzzles_eprime_param_mapping.json') as json_file:
        eprime_param_mapping = json.load(json_file)
        pickle_all_demystify_puzzles(eprime_param_mapping, output_folder=None, ignored=encoded_puzzles)
    # extract_problem_size("pyexplain/examples/demistify/pickles/")
    # pickle_demistify_puzzle(
    #     filename=Path(args.eprime).name + "_" + Path(args.eprimeparam).name + ".json",
    #     problem_name=args.eprime,
    #     param_name=args.eprimeparam,
    #     p_clauses=p_clauses,
    #     p_ass=p_ass,
    #     p_weights=p_weights,
    #     p_user_vars=p_user_vars
    # )
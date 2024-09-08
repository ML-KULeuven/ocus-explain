from pathlib import Path
from pyexplain.solvers.params import BestStepParams
import json 

def to_json_expl(f, explanation, matching_table=None):
    if matching_table is None:
        return explanation

    constraints = list(explanation["constraints"])
    derived = list(explanation["derived"])

    json_explanation = {
        "cost": sum(f(l) for l in constraints),
        "clue": None,
        "assumptions": [],
        "derivations": []
    }



    for fact in derived:
        json_fact = matching_table['bvRel'][abs(fact)]
        json_fact["value"] = True if fact > 0 else False
        json_explanation["derivations"].append(json_fact)

    clue = []
    nTrans = 0
    nBij = 0
    nClue = 0

    for c in constraints:
        if(c in matching_table['Transitivity constraint']):
            nTrans += 1
        elif(c in matching_table['Bijectivity']):
            nBij += 1
        elif(c in matching_table['clues']):
            nClue += 1
            clue.append(matching_table['clues'][c])
        else:
            json_fact = matching_table['bvRel'][abs(c)]
            json_fact["value"] = True if c > 0 else False
            json_explanation["assumptions"].append(json_fact)


    if nClue == 0:
        if nTrans == 0 and nBij == 1:
            json_explanation["clue"] = "Bijectivity"
        elif nTrans == 1 and nBij == 0:
            json_explanation["clue"] = "Transitivity constraint"
        else:
            json_explanation["clue"] = "Combination of logigram constraints"
    elif nClue == 1:
        if nTrans + nBij >= 1:
            json_explanation["clue"] = "Clue and implicit Constraint"
        else:
            json_explanation["clue"] = clue[0]
    else:
        json_explanation["clue"] = "Multiple clues"

    return json_explanation


def export_explanations(explanation_sequence, f, fname, matching_table=None):

    if not Path(fname).parent.exists():
        Path(fname).parent.mkdir()

    file_path = Path(fname)
    json_explanations = []

    for explanation in explanation_sequence:
        json_explanation = to_json_expl(f, explanation, matching_table)
        json_explanations.append(json_explanation)

    with file_path.open('w') as fp:
        json.dump(json_explanations, fp, indent=2)

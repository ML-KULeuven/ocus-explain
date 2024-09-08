
from pathlib import Path
exps = "/Users/emiliogamba/Documents/GitHub/hpc_experiments2/experiments/data/output/SUDOKU_DIFFICULT/2022010516/"
files = sorted([p.name.replace('.json', '').replace('greedy_SUDOKU_DIFFICULT__results_', '') for p in Path(exps).iterdir() if p.is_file() and p.suffix == '.json'])

for i in range(800):
    if str(i) not in files:
        print(f"sbatch greedy_SUDOKU_DIFFICULT__job_{i}.sbatch")
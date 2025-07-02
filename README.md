# Efficiently Explaining CSPs with Unsatisfiable Subset Optimization

This repo contains the code of two papers: the conference version at IJCAI 2021 and the journal version at JAIR 2023.

# JAIR 2023 code

The repo with code and notebooks to run the experiments can be found in `jair2023/`, the code itself is in `jair2023/code/`.

We highly recommend using this (newer) version of the code!


# IJCAI 2021 code

The rest of this README is about the code to the paper accepted at IJCAI 21 [Efficiently Explaining CSPs with Unsatisfiable Subset Optimization](https://arxiv.org/pdf/2105.11763).

To cite this paper, add the following temporary entry:

    @misc{gamba2021efficiently,
      title={Efficiently Explaining CSPs with Unsatisfiable Subset Optimization}, 
      author={Emilio Gamba and Bart Bogaerts and Tias Guns},
      year={2021},
      eprint={2105.11763},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
    }

## Abstract

We build on a recently proposed method for explaining solutions of constraint satisfaction problems. An explanation here is a sequence of simple inference steps, where the simplicity of an inference step is measured by the number and types of constraints and facts used, and where the sequence explains all logical consequences of the problem. We build on these formal foundations and tackle two emerging questions, namely how to generate explanations that are provably optimal (with respect to the given cost metric) and how to generate them efficiently. To answer these questions, we develop:

1) an implicit hitting set algorithm for finding optimal unsatisfiable subsets; 
2) a method to reduce multiple calls for (optimal) unsatisfiable subsets to a single call that takes constraints on the subset into account, and 
3) a method for re-using relevant informationover multiple calls to these algorithms. 

The method is also applicable to other problems that require finding cost-optimal unsatiable subsets. We specifically show that this approach can be used to effectively find sequences of optimal explanation steps for constraint satisfaction problems like logic grid puzzles.

## Installation

Clone repo with the following to update CPMpy's submodule:

```bash
git clone <link-to-ocus-explain-repo> --recurse-submodules
cd ocus-explain/cppy
git submodule update
```

The code also requires the following packages to be installed using pip:

    pip install numpy pandas scipy gurobipy python-sat

## Generating explanations

*A trivial example*

The file `simple_explanations.py` file contains a simple example of an explanation sequence generated.

    python3 simple_explanations.py

### Logic grid puzzles

The different configurations of the paper are testable in `test_explanations.py`. Every parameter configuration is loaded by default with the best configuration.
Change the lines `12` and `13` to test the different puzzles as well as the different configurations.

    python3 test_explanations.py

### Command line interface

For the other puzzles used in the paper, `run_puzzle.py` contains a command-line interface for running the puzzles with a set of given parameters.

## Experiments

The experiments for the paper are generated using `generate_experiments.py` which generates all possible parameter configurations for the different explanation computers (OCUS, OUS, MUS).

THe file generates a `bash` script file in a given input-folder to run the different configurations with a timeout of 2 hours. Once the results are generated, the results can be visualized using the notebook at `benchmark/benchmark_reuseSS.ipynb`, which requires only the path of the output folder to be specified.

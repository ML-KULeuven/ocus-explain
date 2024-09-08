import sys, os
sys.path.insert(0, os.path.abspath('/home/emilio/research/CPMpy/'))

from cpmpy import *
from cpmpy.solvers.pysat import CPM_pysat
from cpmpy.solvers.ortools import CPM_ortools
import numpy as np

# TODO: Encode linear constraint in Bool version

# Variables (one per row)
x1 = intvar(0, 4, name="x1")
x2 = intvar(0, 2, name="x2")
x3 = intvar(0, 3, name="x3")
# x1, x2 = intvar(1,3, shape=2, name="queens")

# Constraints on columns and left/right diagonal
m = Model(
    3*x1 + 2*x2 + 5*x3 <= 12,
)

print(m.constraints)
print(CPM_ortools(m).solve())
print([x1.value(), x2.value(), x3.value()])
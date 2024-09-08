from enum import Enum

class Assumptions(Enum):
    # OPT ="OPT"
    BASE = "BASE"

class Grow(Enum):
    IGNORE = "IGNORE"

class MCS(Enum):
    MCSLS = "MCSLS"
    LBX = "LBX"
    IGNORE = "IGNORE"

class SMUSParams(object):
    def __init__(self):
        self.assumptions = Assumptions.BASE
        self.grow_ext = Grow.IGNORE
        self.mcses = MCS.IGNORE

    def checkparams(self):
        if self.assumptions:
            assert self.assumptions in list(Assumptions)
        if self.grow_ext:
            assert self.grow_ext in list(Grow)

    def __str__(self):
        return f"assumptions = {self.assumptions.name}\ngrow = {self.grow_ext.name}\nmcses = {self.mcses.name}"

    def to_dict(self):
        return {
            "param_assumptions": self.assumptions.name,
            "param_grow": self.grow_ext.name,
            "param_mcses": self.mcses.name
        }

class STATS(object):
    def __init__(self):
        # number of calls
        self.n_hs = 0
        self.n_grow = 0
        self.n_mcses = 0
        self.n_H = 0
        self.H = []

    def to_dict(self):
        return {
            "n_hs": self.n_hs,
            "n_grow": self.n_grow,
            "n_mcses": self.n_mcses,
            "n_H": self.n_H,
            "mcses": self.H
        }

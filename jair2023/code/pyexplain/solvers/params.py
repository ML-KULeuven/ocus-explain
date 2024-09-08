from enum import Enum


class Grow(Enum):
    DISABLED = "DISABLED"
    SAT = "SAT"
    SUBSETMAX = "SUBSETMAX"
    MAXSAT = "MAXSAT"
    DISJ_MCS = "DISJ_MCS"
    CONSTRAINT_DISJ_MCS = "CONSTRAINT_DISJ_MCS"
    CORR_GREEDY = "CORR_GREEDY"
    CORRECTION_SUBSETS_SAT="CORRECTION_SUBSETS_SAT"
    CORRECTION_SUBSETMAX_SAT="CORRECTION_SUBSETMAX_SAT"

class Interpretation(Enum):
    INITIAL = "INITIAL"
    ACTUAL = "ACTUAL"
    FULL = "FULL"
    FINAL = "FINAL"

class Weighing(Enum):
    POSITIVE = "POSITIVE"
    INVERSE = "INVERSE"
    UNIFORM = "UNIFORM"

class HittingSetSolver(Enum):
    HITMAN = "HITMAN"
    MIP = "MIP"

class DisjointMCSes(Enum):
    DISJ_CORR_PREPROCESSING_ONLY = "DISJ_CORR_PREPROCESSING_ONLY"
    DISJ_CORR_BOOTSTRAP_ALL = "DISJ_CORR_BOOTSTRAP_ALL"
    GREEDY_CORR_PREPROCESSING_ONLY = "GREEDY_CORR_PREPROCESSING_ONLY"
    GREEDY_CORR_BOOTSTRAP_ALL = "GREEDY_CORR_BOOTSTRAP_ALL"
    DISABLED = "DISABLED"

class ExplanationComputer(Enum):
    MUS = "MUS"
    OUS_SS = "OUS_SS"
    OUS_NO_OPT = "OUS_NO_OPT"
    OUS_INCREMENTAL_NAIVE = "OUS_INCREMENTAL_NAIVE"
    OUS_INCREMENTAL_NAIVE_PARALLEL = "OUS_INCREMENTAL_NAIVE_PARALLEL"
    OUS_NAIVE_PARALLEL = "OUS_NAIVE_PARALLEL"
    OUS_INCREMENTAL_SHARED = "OUS_INCREMENTAL_SHARED"
    OCUS = "OCUS"
    OCUS_SUBSETS="OCUS_SUBSETS"
    OCUS_NOT_INCREMENTAL = "OCUS_NOT_INCREMENTAL"
    OCUS_NOT_INCREMENTAL_HS = "OCUS_NOT_INCREMENTAL_HS"
    OPTUX_HITMAN = "OPTUX_HITMAN"
    COPTUX = "COPTUX"

class BaseParams(object):
    """
    docstring
    """
    def __init__(self):
        # output
        self.output = ""
        self.instance = ""
        self.timeout = None
        self.explanation_computer = None


    def checkParams(self):
        assert self.instance is not None and len(self.instance) > 0, "Non empty input file"
        assert self.output is not None and len(self.output) > 0, "Non empty output file"
        assert self.explanation_computer is not None, "Non empty explanation computer!"
        assert self.explanation_computer in ExplanationComputer, f"Select from {list(ExplanationComputer)}"

    def to_dict(self):
        return {
            # base parameters
            "output": self.output,
            "instance": self.instance,
            "timeout": self.timeout,
            # type of explanations
            "explanation_computer": self.explanation_computer.name if self.explanation_computer else "" ,

            # grow type for everything except MUS
            "grow": None,
            "maxsatpolarity": None,
            "interpretation": None,
            "weighing": None,
            # implementation specific
            "reuse_SSes": None,
            "sort_literals": None,
            # optux related explnaations
            "disable_disjoint_mcses": None, 
            "disjoint_mcses": None, 
            "disjoint_mcs_interpretation": None, 
            "disjoint_mcs_weighing": None, 
        }

class OptUxParams(BaseParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OPTUX_HITMAN
        self.disable_disjoint_mcses = False

    def to_dict(self):
        d = super().to_dict()
        d["disable_disjoint_mcses"] = self.disable_disjoint_mcses
        return d

class COptUxParams(BaseParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.COPTUX
        self.disable_disjoint_mcses = False

    def to_dict(self):
        d = super().to_dict()
        d["disable_disjoint_mcses"] = self.disable_disjoint_mcses
        return d

class MUSParams(BaseParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.MUS

class BestStepParams(BaseParams):
    """
    docstring
    """
    def __init__(self):
        # output
        super().__init__()

        # grow: ["sat", "subsetmax", "maxsat"]
        self.grow = None

        # MAXSAT growing
        self.maxsat_polarity = False

        # MAXSAT+subset max growing ["initial", "actual", "full"]
        self.interpretation = None

        # Maxsat weighing scheme ["positive", "inverse", "uniform"]
        self.maxsat_weighing = None

        # incremental = reuse of satisfiable subsets with internal structure
        self.reuse_SSes = False

        self.sort_literals = False

        self.disjoint_mcses = None
        self.disjoint_mcs_interpretation = Interpretation.ACTUAL
        self.disjoint_mcs_weighing = Weighing.UNIFORM

    def checkParams(self):
        super().checkParams()
        if self.grow:
            assert self.grow in Grow, f"Wrong parameter: grow= {self.grow} available: {list(Grow)} "

        if self.grow in [Grow.CORR_GREEDY, Grow.MAXSAT]:
            assert self.maxsat_weighing is not None, f"Select weighing, available:[{list(Weighing)}]"
            assert self.maxsat_weighing in Weighing, f"Wrong parameter: weighing= {self.maxsat_weighing} available: {list(Weighing)}"
            assert self.interpretation in Interpretation, f"Wrong parameter: interpretation= {self.interpretation} available: {list(Interpretation)} "

        if  self.grow is Grow.DISJ_MCS or self.disjoint_mcses in [DisjointMCSes.DISJ_CORR_PREPROCESSING_ONLY, DisjointMCSes.DISJ_CORR_BOOTSTRAP_ALL]:
            assert self.disjoint_mcs_interpretation in Interpretation, f"Wrong parameter: interpretation= {self.disjoint_mcs_interpretation} available: {list(Interpretation)} "
            assert self.disjoint_mcs_weighing in Weighing, f"Wrong parameter: weighing= {self.disjoint_mcs_weighing} available: {list(Weighing)}"
            assert (self.grow is Grow.DISJ_MCS or self.disjoint_mcses) and self.disjoint_mcs_weighing is not None and self.disjoint_mcs_interpretation is not None, "Wrong disj. mcs-parameter!"
        if self.disjoint_mcses in [DisjointMCSes.GREEDY_CORR_BOOTSTRAP_ALL, DisjointMCSes.GREEDY_CORR_PREPROCESSING_ONLY]:
            assert self.maxsat_weighing is not None, f"Select weighing, available:[{list(Weighing)}]"
            assert self.maxsat_weighing in Weighing, f"Wrong parameter: weighing= {self.maxsat_weighing} available: {list(Weighing)}"
            assert self.interpretation in Interpretation, f"Wrong parameter: interpretation= {self.interpretation} available: {list(Interpretation)} "

    def to_dict(self):
        d = super().to_dict()
        # execution params
        d["grow"] = self.grow.name  if self.grow else ""
        d["maxsatpolarity"] = self.maxsat_polarity
        d["interpretation"] = self.interpretation.name if self.interpretation else ""
        d["weighing"] = self.maxsat_weighing.name if self.maxsat_weighing else ""
        d["disjoint_mcses"] = self.disjoint_mcses.name  if self.disjoint_mcses else ""
        d["disjoint_mcs_interpretation"] = self.disjoint_mcs_interpretation.name  if self.disjoint_mcs_interpretation else ""
        d["disjoint_mcs_weighing"] = self.disjoint_mcs_weighing.name if self.disjoint_mcs_weighing else ""

        # setup specific parameters
        d["reuse_SSes"] = self.reuse_SSes
        d["sort_literals"] = self.sort_literals

        return d

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class COusParams(BestStepParams):
    def __init__(self):
        # reinitialising the HS solver at every OUS call
        super().__init__()
        self.explanation_computer = ExplanationComputer.OCUS
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class COusSubsetParams(BestStepParams):
    def __init__(self):
        # reinitialising the HS solver at every OUS call
        super().__init__()
        self.explanation_computer = ExplanationComputer.OCUS_SUBSETS
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class COusNonIncrParams(BestStepParams):
    def __init__(self):
        # reinitialising the HS solver at every OUS call
        super().__init__()
        self.explanation_computer = ExplanationComputer.OCUS_NOT_INCREMENTAL
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class COusNonIncrHSParams(BestStepParams):
    def __init__(self):
        # reinitialising the HS solver at every OUS call
        super().__init__()
        self.explanation_computer = ExplanationComputer.OCUS_NOT_INCREMENTAL_HS
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True


class OusNoOptParams(BestStepParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OUS_NO_OPT
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.reuse_SSes = True
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.reuse_SSes = True
        self.maxsat_polarity = True

class OusParams(BestStepParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OUS_SS
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.reuse_SSes = False
        self.sort_literals = True
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.reuse_SSes = False
        self.sort_literals = True
        self.maxsat_polarity = True

class OusIncrNaiveParams(BestStepParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OUS_INCREMENTAL_NAIVE
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class OUSParallelIncrNaiveParams(BestStepParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OUS_INCREMENTAL_NAIVE_PARALLEL
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class OUSParallelNaiveParams(BestStepParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OUS_NAIVE_PARALLEL
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

class OusIncrSharedParams(BestStepParams):
    def __init__(self):
        super().__init__()
        self.explanation_computer = ExplanationComputer.OUS_INCREMENTAL_SHARED
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True


    def load_best_params(self):
        self.grow = Grow.MAXSAT
        self.maxsat_weighing = Weighing.UNIFORM
        self.interpretation = Interpretation.ACTUAL
        self.maxsat_polarity = True

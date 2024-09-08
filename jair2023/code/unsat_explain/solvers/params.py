from enum import Enum

class UNSATExplanationComputer(Enum):
    MUS = "MUS"
    OCUS = "OCUS"
    OCUS_NOT_INCREMENTAL = "OCUS_NOT_INCREMENTAL"

class UNSATBaseParams(object):
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
        assert self.explanation_computer is not None, "Non empty explanation computer!"
        assert self.explanation_computer in UNSATExplanationComputer, f"Select from {list(UNSATExplanationComputer)}"

    def to_dict(self):
        return {
            # base parameters
            "output": self.output,
            "instance": self.instance,
            "timeout": self.timeout,
            # type of explanations
            "explanation_computer": self.explanation_computer.name if self.explanation_computer else "" ,
        }



class UNSATBestStepParams(UNSATBaseParams):
    """
    Explanation of UNSAT
    """
    def __init__(self):
        """
        TODO: UPDATE if params are added
        """
        # output
        super().__init__()

    def checkParams(self):
        """
        TODO: UPDATE if params are added
        """
        super().checkParams()

    def to_dict(self):
        return super().to_dict()

    def load_best_params(self):
        """"
        TODO: UPDATE if params are added
        """
        pass

class UNSATMUSParams(UNSATBestStepParams):
    def __init__(self):
        """
        TODO: UPDATE if params are added
        """
        super().__init__()
        self.explanation_computer = UNSATExplanationComputer.MUS

    def load_best_params(self):
        """"
        TODO: UPDATE if params are added
        """
        pass

class UNSATCOusParams(UNSATBestStepParams):
    def __init__(self):
        # reinitialising the HS solver at every OUS call
        super().__init__()
        self.explanation_computer = UNSATExplanationComputer.OCUS

    def load_best_params(self):
        """"
        TODO: UPDATE if params are added
        """
        pass


class UNSATCOusNonIncrParams(UNSATBestStepParams):
    def __init__(self):
        # reinitialising the HS solver at every OUS call
        super().__init__()
        self.explanation_computer = UNSATExplanationComputer.OCUS_NOT_INCREMENTAL

    def load_best_params(self):
        """"
        TODO: UPDATE if params are added
        """
        pass
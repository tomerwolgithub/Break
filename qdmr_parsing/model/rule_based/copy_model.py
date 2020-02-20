
from model.model_base import ModelBase


class CopyModel(ModelBase):
    def __init__(self):
        super(CopyModel, self).__init__()

    def _decompose(self, question, verbose=False):
        decomposition = [question]
        trace = []

        return decomposition, trace

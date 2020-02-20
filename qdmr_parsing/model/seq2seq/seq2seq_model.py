
import json
import os

from allennlp.models.archival import load_archive
from allennlp.service.predictors import Predictor

from evaluation.decomposition import Decomposition, get_decomposition_from_tokens
from model.model_base import ModelBase

from dataset_readers.simple_seq2seq_dynamic import Seq2SeqDynamicDatasetReader
from model.seq2seq.simple_seq2seq_dynamic import SimpleSeq2SeqDynamic
from model.seq2seq.simple_seq2seq_dynamic_predictor import Seq2SeqDynamicPredictor


class Seq2seqModel(ModelBase):
    def __init__(self, model_dir, model_type, beam, cuda_device=-1):
        super(Seq2seqModel, self).__init__()

        archive_path = os.path.join(model_dir, 'model.tar.gz')
        assert os.path.exists(model_dir)
        assert os.path.exists(archive_path)
        assert model_type in ["seq2seq", "copynet", "dynamic"]

        self.model_dir = model_dir
        self.model_type = model_type
        self.beam = beam

        archive = load_archive(archive_path, cuda_device=cuda_device)
        if self.model_type == "dynamic":
            self.predictor = Seq2SeqDynamicPredictor.from_archive(archive, 'seq2seq_dynamic')
        else:
            self.predictor = Predictor.from_archive(archive, 'seq2seq')

    def _decompose(self, question, verbose):
        pred = self.predictor.predict_json({"source": question})

        if self.beam:
            decomposition = get_decomposition_from_tokens(pred["predicted_tokens"][0])
        else:
            decomposition = get_decomposition_from_tokens(pred["predicted_tokens"])

        return Decomposition(decomposition)

    def predict(self, questions, print_non_decomposed, verbose, extra_args=None):
        # extra_args is used here to pass allowed tokens for the dynamic seq2seq model.
        if extra_args:
            inputs = [{"source": question, "allowed_tokens": allowed_tokens}
                      for question, allowed_tokens in zip(questions, extra_args)]
        else:
            inputs = [{"source": question} for question in questions]
        preds = self.predictor.predict_batch_json(inputs)

        return self._get_decompositions_from_predictions(preds)

    def _get_decompositions_from_predictions(self, preds):
        if self.beam:
            decompositions = [
                get_decomposition_from_tokens(pred["predicted_tokens"][0])
                for pred in preds
            ]
        else:
            decompositions = [
                get_decomposition_from_tokens(pred["predicted_tokens"])
                for pred in preds
            ]

        return decompositions

    def load_decompositions_from_file(self, predictions_file):
        with open(predictions_file, "r") as fd:
            preds = [json.loads(line) for line in fd.readlines()]

        return self._get_decompositions_from_predictions(preds)


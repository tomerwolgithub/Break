
import numpy as np
import neuralcoref
import pandas as pd
import spacy

from evaluation.decomposition import Decomposition
from evaluation.graph_matcher import GraphMatchScorer, get_ged_plus_scores
from evaluation.sari_hook import get_sari
from evaluation.sequence_matcher import SequenceMatchScorer


class ModelBase(object):
    def __init__(self):
        self.parser = spacy.load('en_core_web_sm')
        coref = neuralcoref.NeuralCoref(self.parser.vocab)
        self.parser.add_pipe(coref, name='neuralcoref')

    def _parse(self, question):
        """Run a spaCy model for dependency parsing, POS tagging, etc."""
        return self.parser(question)

    def _decompose(self, question, verbose):
        raise NotImplementedError

    def load_decompositions_from_file(self, predictions_file):
        raise NotImplementedError

    def predict(self, questions, print_non_decomposed, verbose, extra_args=None):
        decompositions = []
        num_decomposed, num_not_decomposed = 0, 0
        for question in questions:
            decomposed, trace = self._decompose(question, verbose)
            if len(decomposed) == 1:
                num_not_decomposed += 1
                if print_non_decomposed:
                    print("question: {}\ndecomposition: -\n".format(question))
            else:
                num_decomposed += 1
                print("question: {}\ndecomposition: {}\ntrace: {}\n".format(question, decomposed, trace))

            decompositions.append(decomposed)

        print("\n{} decomposed questions, {} not-decomposed questions.\n".format(num_decomposed, num_not_decomposed))
        return [Decomposition(d) for d in decompositions]

    @staticmethod
    def print_first_example_scores(evaluation_dict, num_examples):
        for i in range(num_examples):
            print("evaluating example #{}".format(i))
            print("\tsource (question): {}".format(evaluation_dict["question"][i]))
            print("\tprediction (decomposition): {}".format(evaluation_dict["prediction"][i]))
            print("\ttarget (gold): {}".format(evaluation_dict["gold"][i]))
            print("\texact match: {}".format(round(evaluation_dict["exact_match"][i], 3)))
            print("\tmatch score: {}".format(round(evaluation_dict["match"][i], 3)))
            print("\tstructural match score: {}".format(round(evaluation_dict["structural_match"][i], 3)))
            print("\tsari score: {}".format(round(evaluation_dict["sari"][i], 3)))
            print("\tGED score: {}".format(
                round(evaluation_dict["ged"][i], 3) if evaluation_dict["ged"][i] is not None
                else '-'))
            print("\tstructural GED score: {}".format(
                round(evaluation_dict["structural_ged"][i], 3) if evaluation_dict["structural_ged"][i] is not None
                else '-'))
            print("\tGED+ score: {}".format(
                round(evaluation_dict["ged_plus"][i], 3) if evaluation_dict["ged_plus"][i] is not None
                else '-'))

    @staticmethod
    def print_score_stats(evaluation_dict):
        print("\noverall scores:")

        for key in evaluation_dict:
            # ignore keys that do not store scores
            if key in ["question", "gold", "prediction"]:
                continue
            score_name, scores = key, evaluation_dict[key]

            # ignore examples without a score
            if None in scores:
                scores_ = [score for score in scores if score is not None]
            else:
                scores_ = scores

            mean_score, max_score, min_score = np.mean(scores_), np.max(scores_), np.min(scores_)
            print("{} score:\tmean {:.3f}\tmax {:.3f}\tmin {:.3f}".format(
                score_name, mean_score, max_score, min_score))

    @staticmethod
    def write_evaluation_output(output_path_base, num_examples, **kwargs):
        # write evaluation summary
        with open(output_path_base + '_summary.tsv', 'w') as fd:
            fd.write('\t'.join([key for key in sorted(kwargs.keys())]) + '\n')
            for i in range(num_examples):
                fd.write('\t'.join([str(kwargs[key][i]) for key in sorted(kwargs.keys())]) + '\n')

        # write evaluation scores per example
        df = pd.DataFrame.from_dict(kwargs, orient="columns")
        df.to_csv(output_path_base + '_full.tsv', sep='\t', index=False)

    def evaluate(self, questions, decompositions, golds, metadata,
                 output_path_base, num_processes):
        decompositions_str = [d.to_string() for d in decompositions]
        golds_str = [g.to_string() for g in golds]

        # calculating exact match scores
        exact_match = [d.lower() == g.lower() for d, g in zip(decompositions_str, golds_str)]

        # evaluate using SARI
        sources = [q.split(" ") for q in questions]
        predictions = [d.split(" ") for d in decompositions_str]
        targets = [[g.split(" ")] for g in golds_str]
        sari, keep, add, deletion = get_sari(sources, predictions, targets)

        # evaluate using sequence matcher
        sequence_scorer = SequenceMatchScorer(remove_stop_words=False)
        match_ratio = sequence_scorer.get_match_scores(decompositions_str, golds_str,
                                                       processing="base")
        structural_match_ratio = sequence_scorer.get_match_scores(decompositions_str, golds_str,
                                                                  processing="structural")

        # evaluate using graph distances
        graph_scorer = GraphMatchScorer()
        decomposition_graphs = [d.to_graph() for d in decompositions]
        gold_graphs = [g.to_graph() for g in golds]

        ged_scores = graph_scorer.get_edit_distance_match_scores(decomposition_graphs, gold_graphs)
        structural_ged_scores = graph_scorer.get_edit_distance_match_scores(decomposition_graphs, gold_graphs,
                                                                            structure_only=True)
        ged_plus_scores = get_ged_plus_scores(decomposition_graphs, gold_graphs,
                                              exclude_thr=5, num_processes=num_processes)

        evaluation_dict = {
            "question": questions,
            "gold": golds_str,
            "prediction": decompositions_str,
            "exact_match": exact_match,
            "match": match_ratio,
            "structural_match": structural_match_ratio,
            "sari": sari,
            "ged": ged_scores,
            "structural_ged": structural_ged_scores,
            "ged_plus": ged_plus_scores
        }
        num_examples = len(questions)
        self.print_first_example_scores(evaluation_dict, min(5, num_examples))
        self.print_score_stats(evaluation_dict)
        print("skipped {} examples when computing ged.".format(
            len([score for score in ged_scores if score is None])))
        print("skipped {} examples when computing structural ged.".format(
            len([score for score in structural_ged_scores if score is None])))
        print("skipped {} examples when computing ged plus.".format(
            len([score for score in ged_plus_scores if score is None])))

        if output_path_base:
            self.write_evaluation_output(output_path_base, num_examples, **evaluation_dict)

        if metadata is not None:
            metadata = metadata[metadata["question_text"].isin(evaluation_dict["question"])]
            metadata["dataset"] = metadata["question_id"].apply(lambda x: x.split("_")[0])
            metadata["num_steps"] = metadata["decomposition"].apply(lambda x: len(x.split(";")))
            score_keys = [key for key in evaluation_dict if key not in ["question", "gold", "prediction"]]
            for key in score_keys:
                metadata[key] = evaluation_dict[key]

            for agg_field in ["dataset", "num_steps"]:
                df = metadata[[agg_field] + score_keys].groupby(agg_field).agg("mean")
                print(df.round(decimals=3))

        return evaluation_dict


import csv
import logging
import numpy as np

from ast import literal_eval
from overrides import overrides
from typing import Dict, List

from allennlp.common.checks import ConfigurationError
from allennlp.common.file_utils import cached_path
from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.fields import TextField, MetadataField, NamespaceSwappingField
from allennlp.data.instance import Instance
from allennlp.data.tokenizers import Token, Tokenizer, WordTokenizer
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@DatasetReader.register("seq2seq_dynamic")
class Seq2SeqDynamicDatasetReader(DatasetReader):
    """
    Read a tsv file containing paired sequences, and create a dataset suitable for a
    ``SimpleSeq2Seq`` model, or any model with a matching API.

    Expected format for each input line: <source_sequence_string>\t<target_sequence_string>

    The output of ``read`` is a list of ``Instance`` s with the fields:
        source_tokens: ``TextField`` and
        target_tokens: ``TextField``

    `START_SYMBOL` and `END_SYMBOL` tokens are added to the source and target sequences.

    Parameters
    ----------
    source_tokenizer : ``Tokenizer``, optional
        Tokenizer to use to split the input sequences into words or other kinds of tokens. Defaults
        to ``WordTokenizer()``.
    target_tokenizer : ``Tokenizer``, optional
        Tokenizer to use to split the output sequences (during training) into words or other kinds
        of tokens. Defaults to ``source_tokenizer``.
    source_token_indexers : ``Dict[str, TokenIndexer]``, optional
        Indexers used to define input (source side) token representations. Defaults to
        ``{"tokens": SingleIdTokenIndexer()}``.
    target_token_indexers : ``Dict[str, TokenIndexer]``, optional
        Indexers used to define output (target side) token representations. Defaults to
        ``source_token_indexers``.
    source_add_start_token : bool, (optional, default=True)
        Whether or not to add `START_SYMBOL` to the beginning of the source sequence.
    delimiter : str, (optional, default="\t")
        Set delimiter for tsv/csv file.
    """
    def __init__(self,
                 source_tokenizer: Tokenizer = None,
                 target_tokenizer: Tokenizer = None,
                 source_token_indexers: Dict[str, TokenIndexer] = None,
                 target_token_indexers: Dict[str, TokenIndexer] = None,
                 source_add_start_token: bool = True,
                 delimiter: str = "\t",
                 separator_symbol: str = "@@SEP@@",
                 lazy: bool = False) -> None:
        super().__init__(lazy)
        self._source_tokenizer = source_tokenizer or WordTokenizer()
        self._target_tokenizer = target_tokenizer or self._source_tokenizer
        self._allowed_tokenizer = self._source_tokenizer
        self._source_token_indexers = source_token_indexers or {"tokens": SingleIdTokenIndexer()}
        self._target_token_indexers = target_token_indexers or self._source_token_indexers
        self._source_add_start_token = source_add_start_token
        self._delimiter = delimiter
        self._separator_symbol = separator_symbol

        # TODO: should explicitly check that the source and target namespaces are the same,
        # or support different namespaces.

    @overrides
    def _read(self, file_path):
        with open(cached_path(file_path), "r") as data_file:
            logger.info("Reading instances from lines in file at: %s", file_path)
            for line_num, row in enumerate(csv.reader(data_file, delimiter=self._delimiter)):
                if len(row) != 3:
                    raise ConfigurationError("Invalid line format: %s (line number %d)" % (row, line_num + 1))
                source_sequence, allowed_sequence, target_sequence = row
                yield self.text_to_instance(source_sequence, allowed_sequence, target_sequence)

    @overrides
    def text_to_instance(self,
                         source_string: str,
                         allowed_string: str,
                         target_string: str = None) -> Instance:  # type: ignore
        # pylint: disable=arguments-differ
        tokenized_source = self._source_tokenizer.tokenize(source_string)
        if self._source_add_start_token:
            tokenized_source.insert(0, Token(START_SYMBOL))
        tokenized_source.append(Token(END_SYMBOL))
        source_tokens_text = [x.text for x in tokenized_source[1:-1]]
        source_field = TextField(tokenized_source, self._source_token_indexers)

        if target_string is not None:
            tokenized_target = self._target_tokenizer.tokenize(target_string)
            tokenized_target.insert(0, Token(START_SYMBOL))
            tokenized_target.append(Token(END_SYMBOL))
            target_field = TextField(tokenized_target, self._target_token_indexers)
            target_tokens_text = [y.text for y in tokenized_target[1:-1]]
        else:
            target_tokens_text = []

        parsed_allowed_string = self._parse_allowed_string(allowed_string, source_tokens_text, target_tokens_text)
        tokenized_allowed = self._allowed_tokenizer.tokenize(parsed_allowed_string)
        tokenized_allowed.insert(0, Token(self._separator_symbol))
        tokenized_allowed.insert(0, Token(END_SYMBOL))
        tokenized_allowed.insert(0, Token(START_SYMBOL))
        allowed_field = TextField(tokenized_allowed, self._source_token_indexers)
        allowed_token_ids = NamespaceSwappingField(tokenized_allowed, "tokens")

        meta_fields = {
            "source_tokens": source_tokens_text,
            "allowed_tokens": [x.text for x in tokenized_allowed]
        }
        fields_dict = {
            "source_tokens": source_field,
            "allowed_tokens": allowed_field,
            "allowed_token_ids": allowed_token_ids,
        }

        if target_string is not None:
            fields_dict["target_tokens"] = target_field
            meta_fields["target_tokens"] = target_tokens_text

            # Sanity check
            for token in meta_fields["target_tokens"]:
                if token not in meta_fields["allowed_tokens"]:
                    logger.info(f"Missing token in allowed tokens: {token}")

        fields_dict["metadata"] = MetadataField(meta_fields)

        return Instance(fields_dict)

    @staticmethod
    def _parse_allowed_string(allowed_string: str,
                              source_tokens_text: List[str],
                              target_tokens_text: List[str]) -> str:
        allowed_tokens = [t.strip() for t in literal_eval(allowed_string) if type(t) == str]
        allowed_tokens = list(set(
            ' '.join(allowed_tokens).split(' ') + source_tokens_text + target_tokens_text
        ))
        return ' '.join(allowed_tokens)


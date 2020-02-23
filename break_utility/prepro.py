'''This file has been modified from https://github.com/shmsw25/DecompRC/tree/master/DecompRC by keeping only the part relevant for the single-hop RC model.'''

import json
import tokenization
import collections
from tqdm import tqdm

from joblib import Parallel, delayed

import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler

from prepro_util import *

title_s = "<title>"
title_e = "</title>"

def get_dataloader(logger, args, input_file, batch_size, tokenizer):
    examples = read_squad_examples(
        logger=logger, input_file=input_file)
    return get_dataloader_given_examples(logger, args, examples, batch_size, tokenizer)

def get_dataloader_given_examples(logger, args, examples, batch_size, tokenizer):
    train_features, n_answers_with_truncated_answers = convert_examples_to_features(
        logger=logger,
        examples=examples,
        tokenizer=tokenizer,
        max_seq_length=args.max_seq_length,
        doc_stride=args.doc_stride,
        max_query_length=args.max_query_length,
        max_n_answers=1)

    logger.info("***** Running evaluation *****")
    logger.info("  Num orig examples = %d", len(examples))
    logger.info("  Num split examples = %d", len(train_features))
    logger.info("  Batch size = %d", batch_size)

    all_input_ids = torch.tensor([f.input_ids for f in train_features], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in train_features], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in train_features], dtype=torch.long)

    
    all_example_index = torch.arange(all_input_ids.size(0), dtype=torch.long)
    dataset = TensorDataset(all_input_ids, all_input_mask, all_segment_ids,
                    all_example_index)
    sampler = SequentialSampler(dataset)

    dataloader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)
    return dataloader, examples, train_features


def read_squad_examples(logger, input_file):

    def _process_sent(sent):
        if type(sent) != str:
            return [_process_sent(s) for s in sent]
        return sent.replace('–', '-').replace('&', 'and').replace('&amp;', 'and')

    input_data = []
    for _input_file in input_file.split(','):
        with open(_input_file, "r", encoding='utf8') as reader:
            this_data = json.load(reader)["data"]
            input_data += this_data
        print("Load {}, have {} data".format(_input_file, len(input_data)))

    def is_whitespace(c):
        if c == " " or c == "\t" or c == "\r" or c == "\n" or ord(c) == 0x202F:
            return True
        return False

    examples = []
    for entry in tqdm(input_data):
        if 'paragraphs' not in entry:
            qa = {'question': entry['question'],
                  'final_answers': entry['final_answers'],
                  'answers': [[] for _ in range(len(entry['context']))],
                  'id': entry['id']}
            entry['paragraphs'] = [{'context': entry['context'], 'qas': [qa]}]

        for paragraph in entry["paragraphs"]:
            context = paragraph['context']
            qas = paragraph['qas']

            if type(context)==str:
                context = [context]
                for i, qa in enumerate(qas):
                    if 'is_impossible' in qa:
                        assert (len(qa['answers'])==0 and qa['is_impossible']) or \
                                (len(qa['answers'])>0 and not qa['is_impossible'])
                    qas[i]["answers"] = [qa["answers"]]
            try:
                assert np.all([len(qa['answers'])==len(context) for qa in qas])
            except Exception:
                from IPython import embed; embed()
                assert False

            context = [c.lower() for c  in context]

            doc_tokens_list, char_to_word_offset_list = [], []
            for paragraph_text in context:
                doc_tokens = []
                char_to_word_offset = []
                prev_is_whitespace = True
                for c in paragraph_text:
                    if is_whitespace(c):
                        prev_is_whitespace = True
                    else:
                        if prev_is_whitespace:
                            doc_tokens.append(c)
                        else:
                            doc_tokens[-1] += c
                        prev_is_whitespace = False
                    char_to_word_offset.append(len(doc_tokens) - 1)
                doc_tokens_list.append(doc_tokens)
                char_to_word_offset_list.append(char_to_word_offset)

            for qa in qas:
                qas_id = qa["id"]
                question_text = qa["question"]
                start_position = None
                end_position = None
                orig_answer_text = None
                switch = 0

                assert len(qa['answers']) == len(context)
                if 'final_answers' in qa:
                    all_answers = qa['final_answers']
                else:
                    all_answers = []
                    for answers in qa['answers']:
                        all_answers += [a['text'] for a in answers]

                if len(all_answers)==0:
                    all_answers = ["None"]

                assert len(all_answers)>0

                original_answers_list, start_positions_list, end_positions_list, switches_list = [], [], [], []
                for (paragraph_text, doc_tokens, char_to_word_offset, answers) in zip( \
                        context, doc_tokens_list, char_to_word_offset_list, qa['answers']):

                    if len(answers)==0:
                        original_answers = [""]
                        start_positions, end_positions = [0], [0]
                        switches = [3]  # 3 means ans not present
                    else:
                        original_answers, switches, start_positions, end_positions = detect_span(\
                                answers, paragraph_text, doc_tokens, char_to_word_offset)
                    original_answers_list.append(original_answers)
                    start_positions_list.append(start_positions)
                    end_positions_list.append(end_positions)
                    switches_list.append(switches)

                examples.append(SquadExample(
                        qas_id=qas_id,
                        question_text=question_text,
                        doc_tokens=doc_tokens_list,
                        orig_answer_text=original_answers_list,
                        all_answers=all_answers,
                        start_position=start_positions_list,
                        end_position=end_positions_list,
                        switch=switches_list))

    return examples


def convert_examples_to_features(logger, examples, tokenizer, max_seq_length,
                    doc_stride, max_query_length, max_n_answers):
    """Loads a data file into a list of `InputBatch`s."""

    def _convert_examples_to_features(example_index, example):
        unique_id = 1000*example_index

        truncated = []
        features = []
        features_with_truncated_answers = []
        counter_n_answers = collections.Counter()

        query_tokens = tokenizer.tokenize(example.question_text)
        
        if len(query_tokens) > max_query_length: 
            query_tokens = query_tokens[0:max_query_length]

        assert len(example.doc_tokens) == len(example.orig_answer_text) == \
            len(example.start_position) == len(example.end_position) == len(example.switch)

        for (doc_tokens, original_answer_text_list, start_position_list, end_position_list, switch_list) in \
                zip(example.doc_tokens, example.orig_answer_text, example.start_position, \
                    example.end_position, example.switch):

            tok_to_orig_index = []
            orig_to_tok_index = []
            all_doc_tokens = []
            for (i, token) in enumerate(doc_tokens):
                orig_to_tok_index.append(len(all_doc_tokens))
                sub_tokens = tokenizer.tokenize(token)
                for sub_token in sub_tokens:
                    tok_to_orig_index.append(i)
                    all_doc_tokens.append(sub_token)

            tok_start_positions = []
            tok_end_positions = []
            
            # The -3 accounts for [CLS], [SEP] and [SEP]
            max_tokens_for_doc = max_seq_length - len(query_tokens) - 3
            _DocSpan = collections.namedtuple(  # pylint: disable=invalid-name
                "DocSpan", ["start", "length"])
            doc_spans = []
            start_offset = 0
            while start_offset < len(all_doc_tokens):
                length = len(all_doc_tokens) - start_offset
                if length > max_tokens_for_doc:
                    length = max_tokens_for_doc
                doc_spans.append(_DocSpan(start=start_offset, length=length))
                if start_offset + length == len(all_doc_tokens):
                    break
                start_offset += min(length, doc_stride)

            truncated.append(len(doc_spans))


            for (doc_span_index, doc_span) in enumerate(doc_spans):
                tokens = []
                token_to_orig_map = {}
                token_is_max_context = {}
                segment_ids = []
                tokens.append("[CLS]")
                segment_ids.append(0)
                for token in query_tokens:
                    tokens.append(token)
                    segment_ids.append(0)
                tokens.append("[SEP]")
                segment_ids.append(0)

                for i in range(doc_span.length):
                    split_token_index = doc_span.start + i
                    token_to_orig_map[len(tokens)] = tok_to_orig_index[split_token_index]

                    is_max_context = _check_is_max_context(doc_spans, doc_span_index,
                                                        split_token_index)
                    token_is_max_context[len(tokens)] = is_max_context
                    tokens.append(all_doc_tokens[split_token_index])
                    segment_ids.append(1)
                tokens.append("[SEP]")
                segment_ids.append(1)

                input_ids = tokenizer.convert_tokens_to_ids(tokens)

                # The mask has 1 for real tokens and 0 for padding tokens. Only real
                # tokens are attended to.
                input_mask = [1] * len(input_ids)

                # Zero-pad up to the sequence length.
                while len(input_ids) < max_seq_length:
                    input_ids.append(0)
                    input_mask.append(0)
                    segment_ids.append(0)

                assert len(input_ids) == max_seq_length
                assert len(input_mask) == max_seq_length
                assert len(segment_ids) == max_seq_length

                start_positions = []
                end_positions = []
                switches = []
                answer_mask = []
                
                features.append(
                    InputFeatures(
                        unique_id=unique_id,
                        example_index=example_index,
                        doc_span_index=doc_span_index,
                        doc_tokens=doc_tokens,
                        tokens=tokens,
                        token_to_orig_map=token_to_orig_map,
                        token_is_max_context=token_is_max_context,
                        input_ids=input_ids,
                        input_mask=input_mask,
                        segment_ids=segment_ids,
                        start_position=start_positions,
                        end_position=end_positions,
                        switch=switches,
                        answer_mask=answer_mask))

                unique_id += 1

        return features, counter_n_answers, truncated
    outputs = [_convert_examples_to_features(example_index, example) for example_index, example in enumerate(tqdm(examples))]

    features, counter_n_answers, truncated = [], collections.Counter(), []
    for (f, c, t) in outputs:
        features += f
        counter_n_answers.update(c)
        truncated += t

    return features, 0


def _improve_answer_span(doc_tokens, input_start, input_end, tokenizer,
                         orig_answer_text):
    """Returns tokenized answer spans that better match the annotated answer."""

    tok_answer_text = " ".join(tokenizer.tokenize(orig_answer_text))

    for new_start in range(input_start, input_end + 1):
        for new_end in range(input_end, new_start - 1, -1):
            text_span = " ".join(doc_tokens[new_start:(new_end + 1)])
            if text_span == tok_answer_text:
                return (new_start, new_end)

    return (input_start, input_end)


def _check_is_max_context(doc_spans, cur_span_index, position):
    """Check if this is the 'max context' doc span for the token."""
    best_score = None
    best_span_index = None
    for (span_index, doc_span) in enumerate(doc_spans):
        end = doc_span.start + doc_span.length - 1
        if position < doc_span.start:
            continue
        if position > end:
            continue
        num_left_context = position - doc_span.start
        num_right_context = end - position
        score = min(num_left_context, num_right_context) + 0.01 * doc_span.length
        if best_score is None or score > best_score:
            best_score = score
            best_span_index = span_index

    return cur_span_index == best_span_index














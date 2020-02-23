"""Utility experiments for Break dataset."""

import sys
import argparse
import logging
import math
import os
import random
import six
import collections
from tqdm import tqdm, trange
import ujson as json
import time, pickle, re, jsonlines
from copy import deepcopy
from types import SimpleNamespace
from functools import partial
from collections import Counter

import en_core_web_sm
import numpy as np
import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler

import tokenization
from modeling import BertConfig, BertForQuestionAnswering

from prepro import get_dataloader
from pred_util import get_predictions

from info_retriever import IR
from utils import normalize_answer, f1_score, exact_match_score, read_file, write_file, get_ent, dirname
from break_utils import compare, to_squad


logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)

RawResult = collections.namedtuple("RawResult",
                                   ["unique_id", "start_logits", "end_logits", "switch"])


def predict(args, model, eval_dataloader, eval_examples, eval_features, device):
    all_results = []

    def _get_raw_results(model1):
        raw_results = []
        for batch in tqdm(eval_dataloader, desc="Evaluating"):
            example_indices = batch[-1]
            batch_to_feed = [t.to(device) for t in batch[:-1]]
            with torch.no_grad():
                batch_start_logits, batch_end_logits, batch_switch = model1(batch_to_feed)

            for i, example_index in enumerate(example_indices):
                start_logits = batch_start_logits[i].detach().cpu().tolist()
                end_logits = batch_end_logits[i].detach().cpu().tolist()
                switch = batch_switch[i].detach().cpu().tolist()
                eval_feature = eval_features[example_index.item()]
                unique_id = int(eval_feature.unique_id)
                raw_results.append(RawResult(unique_id=unique_id,
                                            start_logits=start_logits,
                                            end_logits=end_logits,
                                            switch=switch))
        return raw_results

    if type(model) == list:
        all_raw_results = [_get_raw_results(m) for m in model]
        for i in range(len(all_raw_results[0])):
            result = [all_raw_result[i] for all_raw_result in all_raw_results]
            assert all([r.unique_id == result[0].unique_id for r in result])
            start_logits = sum([np.array(r.start_logits) for r in result]).tolist()
            end_logits = sum([np.array(r.end_logits) for r in result]).tolist()
            switch = sum([np.array(r.switch) for r in result]).tolist()
            all_results.append(RawResult(unique_id=result[0].unique_id,
                                         start_logits=start_logits,
                                         end_logits=end_logits,
                                         switch=switch))
    else:
        all_results = _get_raw_results(model)

    return get_predictions(logger, eval_examples, eval_features, all_results,
                    args.n_best_size,
                    args.max_answer_length,
                    args.do_lower_case,
                    args.verbose_logging)


def _simpQA(data_list, args, rc_args, tokenizer, model, device):
    tempfile = f'{args.data_dir}/temp_{random.randint(0,1000)}.json'
    write_file({'data': data_list}, tempfile)
    eval_dataloader, eval_examples, eval_features = get_dataloader(logger, args=rc_args, input_file=tempfile,
                                                                   batch_size=args.predict_batch_size, tokenizer=tokenizer)
    os.remove(tempfile)
    preds, nbest = predict(rc_args, model, eval_dataloader, eval_examples, eval_features, device)
    id_preds, id_text_n_logit = {}, {}
    for key, val in preds.items():
        id_preds[key] = val[0]
    for key, val in nbest.items():
        id_text_n_logit[key] = {x['text']:x['logit'] for x in val}
    return id_preds, id_text_n_logit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default='./data', 
                        type=str, help="Data dir containing model dir, etc.")
    parser.add_argument("--tfidf_file", default='wiki_first_paras-tfidf-ngram=2-hash=16777216-tokenizer=spacy.npz', 
                        type=str, help="td-idf .npz file placed inside the data_dir.")
    parser.add_argument("--wiki_jsonl", default='wiki_firstpara_sents.jsonl', 
                        type=str, help="Processed wikipedia .jsonl placed inside data_dir.")
    parser.add_argument("--qdmr_jsonl", default='./data/qdmr_data/qdmrs_hotpotqa_gold.jsonl', 
                        type=str, help="Path to processed qdmr .jsonl file.")
    parser.add_argument("--predict_batch_size", default=128, 
                        type=int, help="Batch size for predictions in eval mode.")
    parser.add_argument("--tasks", default='break_rc,ques_ir,break_ir', 
                        type=str, help="The IR, RC tasks to perform.")
    parser.add_argument("--suffix", default='gold', 
                        type=str, help="Suffix to add to the output files.")
    parser.add_argument("--debug", action='store_true', help="If on, only keep a small number of qdmrs.")
    parser.add_argument("--input_results_file", default='', type=str, 
                        help="File containing results of the task to be reused.")
    args = parser.parse_args()
    
    # we use an already finetuned single-hop RC ensemble by 
    # Min et al (https://github.com/shmsw25/DecompRC/tree/master/DecompRC)
    rc_args = {'bert_config_file': 'data/onehop_rc/uncased_L-12_H-768_A-12/bert_config.json', 
            'do_lower_case': True, 'doc_stride': 128, 'init_checkpoint': f'{args.data_dir}/onehop_rc/uncased_L-12_H-768_A-12/model1.pt,{args.data_dir}/onehop_rc/uncased_L-12_H-768_A-12/model2.pt,{args.data_dir}/onehop_rc/uncased_L-12_H-768_A-12/model3.pt',
            'iterations_per_loop': 1000, 'local_rank': -1, 'max_answer_length': 30, 
            'max_n_answers': 5, 'max_query_length': 64, 'max_seq_length': 300, 'model': 'qa', 
            'n_best_size': 4, 'no_cuda': False, 'output_dropout_prob': 0, 'pooling':'max', 
            'seed': 42, 'verbose_logging': False, 
            'vocab_file': 'data/onehop_rc/uncased_L-12_H-768_A-12/vocab.txt', 'with_key': False}
    rc_args = SimpleNamespace(**rc_args)
    
    # load hotpotQA
    logging.info(f'loading datasets from {args.data_dir}/hotpot_data/ ...')
    data = read_file(f'{args.data_dir}/hotpot_data/hotpot_train_v1.json')
    #data += read_file(f'{args.data_dir}/hotpot_data/hotpot_dev_distractor_v1.json')
    data += read_file(f'{args.data_dir}/hotpot_data/hotpot_dev_fullwiki_v1.json')
    for d in data:
        d['gold_titles'] = {x[0] for x in d['supporting_facts']}
    hotpot = {d['_id']:d for d in data}
    
    # load qdmr data processed using prepare_break.jsonl
    qdmr_path = args.qdmr_jsonl
    logging.info(f'loading processed qdmr data from {qdmr_path} ...')
    qdmrs = read_file(qdmr_path)
    
    # load spacy
    nlp = en_core_web_sm.load()  # spacy 
    tokenize = lambda s: [x.text for x in nlp.tokenizer(s)]

    # load IR
    logging.info('loading IR ...')
    ranker = IR(tfidf_path=f'{args.data_dir}/{args.tfidf_file}')

    # load wikipedia
    wiki_path = f'{args.data_dir}/{args.wiki_jsonl}'
    logging.info(f'loading wikipedia from {wiki_path} ...')
    with jsonlines.open(wiki_path, 'r') as reader:
        wiki = {d['title']: d['para'] for d in tqdm(reader.iter())}
    
    # prepare and load the RC for inference
    device = torch.device("cuda")
    n_gpu = torch.cuda.device_count()
    logging.info(f'{n_gpu} cuda devices available.')
    logging.info('loading 1-hop RC ensemble ...')
    
    random.seed(rc_args.seed)
    np.random.seed(rc_args.seed)
    torch.manual_seed(rc_args.seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(rc_args.seed)

    tokenizer = tokenization.FullTokenizer(
        vocab_file=rc_args.vocab_file, do_lower_case=rc_args.do_lower_case)

    bert_config = BertConfig.from_json_file(rc_args.bert_config_file)
    model = BertForQuestionAnswering(bert_config, 4)

    if rc_args.init_checkpoint is not None:
        model = [model]
        for i, checkpoint in enumerate(rc_args.init_checkpoint.split(',')):
            if i > 0:
                model.append(BertForQuestionAnswering(bert_config, 4))
            logging.info(f"Loading from {checkpoint}")
            state_dict = torch.load(checkpoint, map_location='cpu')
            filter = lambda x: x[7:] if x.startswith('module.') else x
            state_dict = {filter(k):v for (k,v) in state_dict.items()}
            model[-1].load_state_dict(state_dict)
            model[-1].to(device)

    if type(model) == list:
        model = [m.eval() for m in model]
    else:
        model.eval()

    # 1hop RC wrapper
    simpQA = partial(_simpQA, args=args, rc_args=rc_args, tokenizer=tokenizer, model=model, device=device)
    
    
    if args.input_results_file:
        logging.info(f'Reading the supplied results file {args.input_results_file} ...')
        all_results = read_file(args.input_results_file)
    else:
        all_results = {}
        for i_d, d in enumerate(qdmrs):
            [_, data_split, _id] = d['question_id'].split('_')
            #assert data_split == 'dev'
            assert _id in hotpot
            all_results[_id] = d
            assert d['steps'] and d['op_types'], print('QDMRs must be pre-processed and non-empty.')
    
    if args.debug:
        all_results = {key:val for key, val in all_results.items() if random.random() < 0.01}
        logging.info(f'\nTruncating to only {len(all_results)} samples!!!\n')
    
    tasks = [x.strip() for x in args.tasks.split(',')]
    
    if 'break_rc' in tasks:
        logging.info(f'Running BREAK IR+RC on {len(all_results)} samples ...')
        max_n_parts = max([len(v['steps']) for v in all_results.values()])
        
        for i_p in range(max_n_parts):
            logging.info(f'Processing qdmr step #{i_p} ...')
            # process the i_p'th part of all samples
            articles = []      # hotpot articles corresponding to queries to the RC
            for _id, v in tqdm(all_results.items()):
                parts = v['steps']
                if i_p >= (len(parts) - int(v['op_types'][-1] in ['COMPARISON', 'INTERSECTION'])): 
                    # the last discrete comparison, intersection step is processed later
                    continue
                rc_outputs = v['rc_outputs'] if 'rc_outputs' in v else {}
                nbest_outputs = v['nbest_outputs'] if 'nbest_outputs' in v else {}
                l_top = v['titles'] if 'titles' in v else []
                part = parts[i_p]
                # replace placeholders with the respective RC outputs of previous parts
                for j in range(i_p):
                    ph = '#'+str(j+1)  # 1...i_p
                    if ph in part:
                        part = part.replace(ph, rc_outputs[ph])
                # get top 10 titles from IR
                top_titles = ranker.closest_docs(part, k=10)[0]
                l_top.append(top_titles)
                v.update({'titles': l_top, 'rc_outputs': rc_outputs, 'nbest_outputs': nbest_outputs})
                context = []
                # use all retrieved para for the sample instead of just current 10 & sort them acc to similarity wrt part
                set_l_top = set(sum(l_top, []))
                scores = ranker.rank_titles(part, set_l_top)
                sorted_l_top = sorted(scores.keys(), key=lambda title: scores[title], reverse=True)
                for title in sorted_l_top:   
                    context.append([title, wiki[title]['sents']]) # get para from wiki
                if not sorted_l_top:
                    # rare case of no valid titles
                    context = [['Random Title 1', 'Random Text 1'], ['Random Title 2', 'Random Text 2']]
                d, article = hotpot[_id], {}
                article['question'], article['context'] = part + ' ?', context  # appending '?' to part query
                article.update({k:d[k] for k in ['_id', 'type', 'answer']})  # '_id', 'type', 'context', 'question', 'answer'
                articles.append(article)
            if not articles:
                continue
            # querying the 1-hop RC
            all_nbest_out = simpQA([to_squad(article) for article in articles])[1]
            for _id, v in all_results.items():
                if _id not in all_nbest_out:
                    continue
                nbest_i_p = all_nbest_out[_id]
                op = v['op_types'][i_p]
                nbest_id = v['nbest_outputs']
                # handle filter steps
                if 'FILTER' in op:
                    ref_ph = op.split('_')[1]
                    nbest_ref = Counter(nbest_id[ref_ph])
                    # accumulating the logits of nbest of the part and the ref part
                    nbest_ref.update(nbest_i_p)
                    nbest_i_p = dict(nbest_ref)
                rc_out = max(nbest_i_p.keys(), key=lambda key: nbest_i_p[key])
                v['rc_outputs'][f'#{i_p+1}'] = rc_out
                v['nbest_outputs'][f'#{i_p+1}'] = nbest_i_p
            
        # discrete processing of the last comparison step
        logging.info(f'Discrete processing of the last comparison/intersection steps ...')
        for _id, v in all_results.items():
            if v['op_types'][-1] not in ['COMPARISON', 'INTERSECTION']:
                continue
            question, answer, gold_titles = hotpot[_id]['question'], hotpot[_id]['answer'], hotpot[_id]['gold_titles']
            parts, rc_outputs = v['steps'], v['rc_outputs']
            if v['op_types'][-1] == 'COMPARISON':
                ents, rc_outs = [], []
                for i_p, part in enumerate(parts[:-1]):
                    # get named entity in the part
                    part_without_phs = part
                    for x in ['#'+str(j) for j in range(1,8)]:
                        part_without_phs = part_without_phs.replace(x, '')
                    ent = get_ent(part_without_phs, nlp, only_longest=True)
                    ent = '' if ent is None else ent
                    ents.append(ent)
                    rc_outs.append(normalize_answer(rc_outputs['#'+str(i_p+1)]))
                if 'same as' in parts[-1]:
                    pred_ans = 'yes' if rc_outs[-2] == rc_outs[-1] else 'no'
                else:
                    pred_ans = ents[compare(parts[-1], rc_outs[-2], rc_outs[-1])]
                    v['rc_outputs'][f'#{len(parts)}'] = pred_ans
            elif v['op_types'][-1] == 'INTERSECTION':
                part = parts[-1]
                phs = ['#'+str(j) for j in range(1,10) if '#'+str(j) in part]
                phs = list(set(phs))
                # accumulate logits of the parts and take the argmax
                nbest_id = v['nbest_outputs']
                nbest = Counter(nbest_id[phs[0]])
                # accumulate logits
                for ph in phs[1:]:
                    if ph in nbest_id:
                        nbest.update(nbest_id[ph])
                nbest = dict(nbest)
                pred_ans = max(nbest.keys(), key=lambda key: nbest[key])
                v['rc_outputs'][f'#{len(parts)}'] = pred_ans
                v['nbest_outputs'][f'#{len(parts)}'] = nbest    
        
        for v in all_results.values():
            assert len(v['rc_outputs']) == len(v['steps'])
            
    
    if 'break_ir' in tasks:
        # this can only be run after break_rc task & requires all_results dict 
        logging.info(f'Forming context using the titles used by Break RC for {len(all_results)} samples ...')
        # prepare hotpot-like data for Bert RC
        new_hotpot = []
        for _id, v in tqdm(all_results.items()):
            d = hotpot[_id]
            d_new = deepcopy(d)
            used_titles = sum(v['titles'], [])
            # sort wrt similarity to ques
            scores = ranker.rank_titles(d['question'], set(used_titles))
            titles = sorted(scores.keys(), key=lambda title: scores[title], reverse=True)            
            context = []
            for title in titles:
                context.append([title, wiki[title]['sents']])
            d_new['context'] = context
            if 'gold_titles' in d_new:
                del d_new['gold_titles']
            new_hotpot.append(d_new)
        out_break_ir_file = f'{args.data_dir}/hotpot_data/hotpot_after_break_ir_{args.suffix}.json'
        logging.info(f'Writing hotpot version with the Break IR context to {out_break_ir_file} ...')
        write_file(new_hotpot, out_break_ir_file)
    
        # store the retrieved titles
        for d in new_hotpot:
            all_results[d['_id']]['titles_found_by_break_rc'] = list(set([x[0] for x in d['context']]))
    
        
    if 'ques_ir' in tasks:
        # this can only be run after break_rc task & requires all_results dict formed 
        # to determine the number of titles to be retrieved for each sample
        logging.info(f'Running baseline IR using the whole question for {len(all_results)} samples ...')
        # prepare hotpot-like data for Bert RC
        new_hotpot = []
        for _id in tqdm(all_results.keys()):
            d = hotpot[_id]
            d_new = deepcopy(d)
             # for fair comparison with Break RC retrieve the same number of titles
            n_titles = len(sum(all_results[_id]['titles'], []))
            titles = ranker.closest_docs(d['question'], k=n_titles)[0]
            context = []
            for title in titles:
                context.append([title, wiki[title]['sents']])
            d_new['context'] = context
            if 'gold_titles' in d_new:
                del d_new['gold_titles']
            new_hotpot.append(d_new)
        out_ques_ir_file = f'{args.data_dir}/hotpot_data/hotpot_after_ques_ir_{args.suffix}.json'
        logging.info(f'Writing hotpot version with the baseline IR context to {out_ques_ir_file} ...')
        write_file(new_hotpot, out_ques_ir_file)
    
        # store the retrieved titles
        for d in new_hotpot:
            all_results[d['_id']]['titles_found_using_whole_ques'] = list(set([x[0] for x in d['context']]))
        
            
    # save the Break RC outputs
    out_break_rc_file = f'{args.data_dir}/predictions/break_rc_results_{args.suffix}.json'
    logging.info(f'Writing the break RC results to {out_break_rc_file}...')
    os.makedirs(dirname(out_break_rc_file), exist_ok=True)
    write_file(all_results, out_break_rc_file)


if __name__ == "__main__":
    main()

'''
CUDA_VISIBLE_DEVICES=3 python run_break.py --qdmr_jsonl ./data/qdmr_data/qdmrs_hotpotqa_gold.jsonl --suffix gold --predict_batch_size 256 --debug
By default this saves: 
break_rc results in ./data/predictions/break_rc_results_gold.json
hotpot for ques_ir + bert_rc in ./data/hotpot_data/hotpot_after_ques_ir_gold.json
hotpot for break_ir + bert_rc in ./data/hotpot_data/hotpot_after_break_ir_gold.json
'''
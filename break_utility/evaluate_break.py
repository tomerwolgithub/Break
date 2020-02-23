"""Evaluating the IR performance, em, f1 of BreakRC, BertRC, BreakIR+BertRC, etc."""

import sys
import argparse
import logging
import os
from tqdm import tqdm, trange
import ujson as json
import time, pickle, re, jsonlines

import numpy as np

from utils import f1_score, exact_match_score, read_file, write_file, dirname

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default='./data', 
                        type=str, help="Data dir containing model dir, etc.")
    parser.add_argument("--input_results_file", default='', type=str, 
                        help="File containing results of the task to be reused.")
    parser.add_argument("--bert_rc_pred_files", default='', type=str, 
                        help="Comma separated list of prediction files outputted by BERT Hotpot model.")
    args = parser.parse_args()
    
    # load hotpotQA
    logging.info(f'loading datasets from {args.data_dir}/hotpot_data/ ...')
    data = read_file(f'{args.data_dir}/hotpot_data/hotpot_train_v1.json')
    #data += read_file(f'{args.data_dir}/hotpot_data/hotpot_dev_distractor_v1.json')
    data += read_file(f'{args.data_dir}/hotpot_data/hotpot_dev_fullwiki_v1.json')
    for d in data:
        d['gold_titles'] = {x[0] for x in d['supporting_facts']}
    hotpot = {d['_id']:d for d in data}
    
    all_results = {}
    if args.input_results_file:
        logging.info(f'Reading the supplied results file {args.input_results_file} ...')
        all_results = read_file(args.input_results_file)
    
    # IR performance 
    if all_results:
        for key in ['titles_found_using_whole_ques', 'titles_found_by_break_rc']:
            n_titles_found = []
            for _id, v in all_results.items():
                if key in v:
                    n_titles_found.append(len(set(v[key]).intersection(hotpot[_id]['gold_titles'])))
            if n_titles_found:
                ir_results = np.unique(n_titles_found, return_counts=True)[1] / len(all_results) * 100
                ir_results = dict(enumerate(ir_results))
                logging.info(f'% of 0/1/2 gold titles in {key} = {ir_results}')
    
    # RC performance
    def get_em_f1(preds):
        em, f1 = [], []
        for _id, pred in preds.items():
            answer = hotpot[_id]['answer']
            f1.append(f1_score(pred, answer))
            em.append(exact_match_score(pred, answer))
        return np.mean(em), np.mean(f1)

    if all_results:
        preds = {}
        for _id, v in all_results.items():
            parts, rc_outputs, answer = v['steps'], v['rc_outputs'], hotpot[_id]['answer']
            preds[_id] = rc_outputs['#'+str(len(parts))]
        em, f1 = get_em_f1(preds)
        logging.info(f'BreakRC eval scores: EM: {em}, F1: {f1} on {len(preds)} samples.')
    
    bert_rc_pred_files = args.bert_rc_pred_files.strip().split(',')
    for bert_rc_pred_file in bert_rc_pred_files:
        if not bert_rc_pred_file:
            continue
        logging.info(f'Reading Bert RC predictions from {bert_rc_pred_file} ...')
        preds = read_file(bert_rc_pred_file)
        em, f1 = get_em_f1(preds)
        logging.info(f'{bert_rc_pred_file} eval scores: EM: {em}, F1: {f1} on {len(preds)} samples.')

    
if __name__ == "__main__":
    main()

'''
python evaluate_break.py --data_dir ./data --input_results_file ./data/predictions/break_rc_results_gold.json --bert_rc_pred_files path1,path2 
'''
"""Rule-based preprocessing of Break QDMR's and determining their operation types."""

import sys
import argparse
import logging
import os
from tqdm import tqdm, trange
import ujson as json
import time, pickle, re, jsonlines

from preprocess import *

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)


def dirname(path):
    '''direc containing the file at path.'''
    direc = os.path.dirname(path)
    return f'{direc}/' if direc else './'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default='../data/qdmr_data/hotpotqa_dev_gold.csv', 
                        type=str, help="path to .csv/.tsv (gold/predicted/rule-based) to be pre-processed.")
    parser.add_argument("--ques_file", default='../data/qdmr_data/hotpotqa_dev_questions.csv', 
                        type=str, help="path to the .csv containing the corresponding questions.")
    parser.add_argument("--output_file", default='processed_data_hotpotqa_gold.csv', 
                        type=str, help="the processed break .csv to be saved in same dir as input_file.")
    parser.add_argument("--is_gold",  action='store_true', help="Whether the input annotations are gold or not.")
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = f'{dirname(input_file)}/{args.output_file}'
    
    logging.info(f'loading {input_file} ...')
    if args.is_gold:
        data = read_gold_qdmrs(input_file)
    else:
        data = read_predicted_qdmrs(input_file, args.ques_file)
        
    processed_qdmr_data(data, output_file)
    logging.info(f'Saved to {output_file}')

if __name__ == "__main__":
    main()

'''
python prepro_break.py --input_file ../data/qdmr_data/hotpotqa_dev_gold.csv --output_file processed_data_hotpotqa_gold.csv --is_gold

python prepro_break.py --input_file ../data/qdmr_data/preds_copynet_hpqa_dev_test.tsv --ques_file ../data/qdmr_data/hotpotqa_dev_questions.csv --output_file processed_data_hotpotqa_copy_net.csv

python prepro_break.py --input_file ../data/qdmr_data/preds_rule_based_high_level_dev.tsv --ques_file ../data/qdmr_data/hotpotqa_dev_questions.csv --output_file processed_data_hotpotqa_rule_based.csv
'''

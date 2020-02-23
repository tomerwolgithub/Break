"""Rule-based preprocessing of Break QDMR's and determining their operation types."""

import sys
import argparse
import collections
import logging
import math
import os
import random
import six
from tqdm import tqdm, trange
import ujson as json
import time, pickle, re, jsonlines
from copy import deepcopy
from functools import partial
from collections import Counter

import numpy as np
import pandas as pd

from utils import read_file, write_file, get_ent, dirname
from break_utils import compare


logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)


DELIMITER = ';'
REF = '#'
FLTR_STR = '@@@FILTER_WITH@@@'


# ---------- rule-based identification of the qdmr ops given the decomposition steps -----------

class QDMROperation:
    FIND, SELECT, FILTER, PROJECT, AGGREGATE, GROUP, SUPERLATIVE, COMPARATIVE, UNION, \
    INTERSECTION, DISCARD, SORT, BOOLEAN, ARITHMETIC, COMPARISON, NONE = range(16)
    
def op_name(qdmr_op):
    return {
        QDMROperation.FIND : 'FIND',
        QDMROperation.SELECT : 'SELECT',
        QDMROperation.FILTER : 'FILTER',
        QDMROperation.PROJECT : 'PROJECT',
        QDMROperation.AGGREGATE : 'AGGREGATE',
        QDMROperation.GROUP : 'GROUP',
        QDMROperation.SUPERLATIVE : 'SUPERLATIVE',
        QDMROperation.COMPARATIVE : 'COMPARATIVE',
        QDMROperation.UNION : 'UNION',
        QDMROperation.INTERSECTION : 'INTERSECTION',
        QDMROperation.DISCARD : 'DISCARD',
        QDMROperation.SORT : 'SORT',
        QDMROperation.BOOLEAN : 'BOOLEAN',
        QDMROperation.ARITHMETIC : 'ARITHMETIC',
        QDMROperation.COMPARISON : 'COMPARISON',
        QDMROperation.NONE : 'NONE'
    }.get(qdmr_op, QDMROperation.NONE)

   
def step_type(step, is_high_level):
    """
    Maps a single QDMR step into relevant its operator type
    
    Parameters
    ----------
    step : str
        String representation a single QDMR step
    is_high_level : bool
        Flag whether or not we include the high level FIND steps,
        associated with RC datasets
    
    Returns
    -------
    QDMROperation
        returns the type of QDMR operation of the step
    """
    step = step.lower()
    references = extract_references(step)
    if any([step.lower().startswith(x) for x in ['if ', 'is ', 'are ']]):
        # BOOLEAN step - starts with either 'if', 'is', 'are'
        return QDMROperation.BOOLEAN
    if len(references) == 0:
        # SELECT step - no references to previous steps
        return QDMROperation.SELECT
    # Discrete QDMR step types:
    if len(references) == 1:
        # AGGREGATION step - aggregation applied to one reference
        aggregators = ['number of', 'highest', 'largest', 'lowest', 'smallest', 'maximum', 'minimum', \
                       'max', 'min', 'sum', 'total', 'average', 'avg', 'mean ']
        for aggr in aggregators:
            aggr_ref = aggr + ' #'
            aggr_of_ref = aggr + ' of #'
            if (aggr_ref in step) or (aggr_of_ref in step):
                return QDMROperation.AGGREGATE
    if 'for each' in step:
        # GROUP step - contains term 'for each'
        return QDMROperation.GROUP
    if len(references) >= 2 and len(references) <= 3 and ('where' in step):
        # COMPARATIVE step - '#1 where #2 is at most three'
        comparatives = ['same as', 'higher than', 'larger than', 'smaller than', 'lower than',\
                        'more', 'less', 'at least', 'at most', 'equal', 'is', 'are', 'was', 'contain', \
                        'include', 'has', 'have', 'end with', 'start with', 'ends with', \
                        'starts with', 'begin']
        for comp in comparatives:
            if comp in step:
                return QDMROperation.COMPARATIVE
    if step.startswith('#') and ('where' in step) and len(references) == 2:
        # SUPERLATIVE step - '#1 where #2 is highest/lowest'
        superlatives = ['highest', 'largest', 'most', 'smallest', 'lowest', 'smallest', 'least', \
                       'longest', 'shortest', 'biggest']
        for s in superlatives:
            if s in step:
                return QDMROperation.SUPERLATIVE
    if len(references) > 1:
        # UNION step - '#1, #2, #3, #4' / '#1 or #2' / '#1 and #2'
        is_union = re.search("^[#\s]+[and0-9#or,\s]+$", step)
        if is_union:
            return QDMROperation.UNION
    if len(references) > 1 and ('both' in step) and ('and' in step):
        # INTERSECTION step - 'both #1 and #2'
        return QDMROperation.INTERSECTION
    if (len(references) >= 1) and (len(references) <= 2) and \
    (re.search("^[#]+[0-9]+[\s]+", step) or re.search("[#]+[0-9]+$", step)) and \
     ('besides' in step or 'not in' in step):
        # DISCARD step - '#2 besides X'
        return QDMROperation.DISCARD
    if ('sorted by' in step) or ('order by' in step) or ('ordered by' in step):
        # SORT step - '#1 ordered/sorted by #2'
        return QDMROperation.SORT
    if step.lower().startswith('which') and len(references) > 1:
        # COMPARISON step - 'which is better A or B or C'
        return QDMROperation.COMPARISON
    if len(references) >= 1 and ('and' in step or ',' in step):
        # ARITHMETIC step - starts with arithmetic operation
        arithmetics = ['sum', 'difference', 'multiplication', 'division']
        for a in arithmetics:
            if step.startswith(a) or step.startswith('the ' + a):
                return QDMROperation.ARITHMETIC
    # Non-discrete QDMR step types:
    if len(references) == 1 and re.search("[\s]+[#]+[0-9\s]+", step):
        # PROJECT step - 'property of #2'
        return QDMROperation.PROJECT
    if len(references) == 1 and step.startswith("#"):
        # FILTER step - '#2 [condition]'
        return QDMROperation.FILTER
    if len(references) > 1 and step.startswith("#"):
        # FILTER step - '#2 [relation] #3'
        return QDMROperation.FILTER
    if is_high_level:
        return QDMROperation.FIND
    return QDMROperation.NONE
    

def extract_references(step):
    """Extracts list of references to previous steps
    
    Parameters
    ----------
    step : str
        String representation of a QDMR step
    
    Returns
    -------
    list
        returns list of ints of referenced steps
    """
    # make sure decomposition does not contain a mere '# ' rather than reference.
    step = step.replace("# ", "hashtag ")
    # replace ',' with ' or'
    step = step.replace(", ", " or ")
    references = []
    l = step.split(REF)
    for chunk in l[1:]:
        if len(chunk) > 1:
            ref = chunk.split()[0]
            ref = int(ref)
            references += [ref]
        if len(chunk) == 1:
            ref = int(chunk)
            references += [ref]
    return references


# ------- preparing the QDMRs based on identified ops -------------

class QDMR:
    def __init__(self, question_id, steps, op_types=None):
        '''Further processing FILTER steps for convenience during downstream tasks. 
        '''
        op_types = op_types if op_types else [get_op_type(step) for step in steps]
        assert len(steps) == len(op_types) and len(steps)
        
        _steps, _op_types = [], []
        for i_s, (step, op) in enumerate(zip(steps, op_types)):
            if FLTR_STR in step:
                # append the index of the step wrt which the filter step is applied
                if step.count(FLTR_STR) > 1:       # hack for rule-based
                    # removing the starting FILTER string
                    step = step[len(FLTR_STR):].strip()
                assert step.count(FLTR_STR) == 1, print(step)
                # --------------
#                 if op != 'FILTER':
#                     print(f'{i_s} : "{step}" : changing identified op {op} --> FILTER')
#                     op = 'FILTER'
                # ----------------
                assert op == 'FILTER', print(op_types, op, step, '\n***********')
                idx = step.index(FLTR_STR)
                # extract the filter string with the operand step idx
                ph = step[idx + len(FLTR_STR):].strip()
                assert ph in [f'#{n}' for n in range(1,7)], print(step, ph)
                assert int(ph[1:]) <= i_s, print(steps, op_types, ph)
                _steps.append(step[:idx].strip())
                _op_types.append(op+str(f'_{ph}'))
            else:
                _steps.append(step)
                _op_types.append(op)
        
        self.question_id = question_id
        self.steps = _steps
        self.op_types = _op_types


def parse_decomposition(qdmr):
    """Parses the decomposition into an ordered list of steps
    
    Parameters
    ----------
    qdmr : str
        String representation of the QDMR
    
    Returns
    -------
    list
        returns ordered list of qdmr steps
    """
    crude_steps = qdmr.split(DELIMITER)
    steps = []
    for step in crude_steps:
        tokens = step.strip().split()
        # remove 'return' prefix
        step = ' '.join([tok.strip() for tok in tokens[1:] if tok.strip()])
        steps.append(step)
    return steps


def prepare_decompositions(csv_path):
    """Reads file of QDMR strings into list of decompositions
    
    Parameters
    ----------
    file_path : str
        Path to the decomposition file
    
    Returns
    -------
    list
        Returns list of QDMR objects
    """
    rows = pd.read_csv(csv_path, encoding='utf8').to_dict(orient='records')
    qdmrs = []
    for i, r in enumerate(rows):
        given_steps = [x.strip() for x in r['steps'].strip().split(DELIMITER)]
        given_types = [x.strip() for x in r['operators'].strip().split(DELIMITER)]
        qdmr = QDMR(r['id'], given_steps, given_types)
        qdmrs.append(qdmr)
    return qdmrs


def get_op_type(step):
    op = step_type(step, True)
    if op == QDMROperation.FIND or \
    op == QDMROperation.PROJECT:
        return "BRIDGE"
    if op == QDMROperation.BOOLEAN:
        refs = extract_references(step)
        if len(refs) == 2:
            if (' both ' in step) and (' and ' in step):
                return '%s_AND' % op_name(op)
            if (' either ' in step) and (' or ' in step):
                return '%s_OR' % op_name(op)
            if (' same as ' in step):
                return '%s_EQ' % op_name(op)
            if (' different ' in step):
                return '%s_NEQ' % op_name(op)     
        return op_name(op)
    else:
        return op_name(op)
    return False


def print_op_stats(qdmr_list):
    has_op_counter = Counter()
    all_ops_counter = Counter()
    for qdmr in qdmr_list:
        has_op_counter.update(set(qdmr.op_types))
        all_ops_counter.update({str(qdmr.op_types)})
    print(f"Num of QDMRs: {len(qdmr_list)}")
    for op, cnt in has_op_counter.most_common():
        print(f"containing a {op} step: {cnt} , {round(cnt / len(qdmr_list) * 100, 2)}%")
    print("*"*50)
    print('Most common op-sequences with a FILTER:')
    for key, count in all_ops_counter.most_common():
        if 'FILTER' in key:
            print(key, '%.2f%%' % (count*100/len(qdmr_list)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed_break_csv", default='data/qdmr_data/processed_data_hotpotqa_gold.csv', 
                        type=str, help="path to the processed .csv of the break experiment (gold/predicted/rule-based).")
    parser.add_argument("--out_jsonl", default='qdmrs_hotpot_gold.jsonl', 
                        type=str, help="the processed break .jsonl to be saved in same dir as input break file.")
    args = parser.parse_args()
    
    break_csv = args.processed_break_csv
    
    # process the QDMRs
    logging.info(f'processing {break_csv} ...')
    qdmrs = prepare_decompositions(break_csv)
    
    # operator statistics
    print_op_stats(qdmrs)
    
    outfile = f'{dirname(break_csv)}/{args.out_jsonl}'
    logging.info(f'saving the processed QDMRs to {outfile}')
    write_file([qdmr.__dict__ for qdmr in qdmrs], outfile)
    

if __name__ == "__main__":
    main()

'''
python prepare_break.py --processed_break_csv data/qdmr_data/processed_data_hotpotqa_gold.csv --out_jsonl qdmrs_hotpotqa_gold.jsonl
python prepare_break.py --processed_break_csv data/qdmr_data/processed_data_hotpotqa_copy_net.csv --out_jsonl qdmrs_hotpotqa_copy_net.jsonl
python prepare_break.py --processed_break_csv data/qdmr_data/processed_data_hotpotqa_rule_based.csv --out_jsonl qdmrs_hotpotqa_rule_based.jsonl
'''

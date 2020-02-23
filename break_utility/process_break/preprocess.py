"""
# @Time    : 2020/2/23
# @Author  : Wolfson
"""
import csv
import pandas as pd
from qdmr_steps import *
from utils import *

# Process decompositions into RC-executable steps

def get_steps_dict(qdmr_steps):
    steps_dict = {}
    count = 1
    for step in qdmr_steps:
        steps_dict[count] = step
        count+=1
    return steps_dict


# Handle FILTER and AGGRGATE ("number of") steps

def handle_filter_steps(qdmr_steps):
    """Changes FILTER steps into RC friendly format.
        It moves the reference of the FILTER to the end of the step,
        replacing the prefix with a noun phrase.
    
    Parameters
    ----------
    qdmr_steps : list
        list of QDMR steps
    
    Returns
    -------
    list
        list of revised QDMR steps
    """
#     print(qdmr_steps)########################
    new_steps = []
    new_steps_dict = {}
    old_steps_dict = get_steps_dict(qdmr_steps)
    n = len(qdmr_steps)
    for i in range(1, n+1):
        step = old_steps_dict[i]
        op_type = get_op_type(step)
        if op_type == "FILTER":
            ref = extract_references(step)[0]
            ref_step = new_steps_dict[ref]
            first_NP = extract_noun_phrases(ref_step)[0]
            full_ref = "#%s" % ref
            # replace the reference with the first NP of the referenced step
            new_step = step.replace(full_ref, first_NP)
            new_step = "%s @@@FILTER_WITH@@@ %s" % (new_step, full_ref)
            new_steps_dict[i] = new_step
        else:
            new_steps_dict[i] = step
    for i in range(1, n+1):
        step = new_steps_dict[i]
        new_steps += [step]
    return new_steps


def handle_count_steps(qdmr_steps):
    """Changes 'number of #x' steps to BRIDGE steps
    
    Parameters
    ----------
    qdmr_steps : list
        list of QDMR steps
    
    Returns
    -------
    list
        list of revised QDMR steps
    """
    new_steps = []
    new_steps_dict = {}
    old_steps_dict = get_steps_dict(qdmr_steps)
    n = len(qdmr_steps)
    for i in range(1, n+1):
        step = old_steps_dict[i]
        op_type = get_op_type(step)
        if op_type == "AGGREGATE" and \
        (step.startswith('the number') or step.startswith('number')):
            ref = extract_references(step)[0]
            ref_step = old_steps_dict[ref]
            new_ref_step = "how many %s" % ref_step
            new_steps_dict[i] = new_ref_step
        else:
            new_steps_dict[i] = step
    for i in range(1, n+1):
        step = new_steps_dict[i]
        new_steps += [step]
    return new_steps


def process_steps(qdmr_steps):
    proc_steps = handle_count_steps(qdmr_steps)
    proc_steps = handle_filter_steps(proc_steps)
    return proc_steps


def replace_ref(qdmr_steps, old_ref, new_ref):
    """
    replaces all the refernces to old step with refrences to the new step
    """
    new_steps = []
    for step in qdmr_steps:
        refernces = extract_references(step)
        for ref in refernces:
            if ref == old_ref:
                step = step.replace('#'+old_ref, '#'+new_ref)
            new_steps += [step]
    return new_steps

def process_predicted_qdmr(predicted_qdmr):
    """Converts a predicted qdmr string to standard qdmr
    E.g., from "the writer of The Bet born @@SEP@@ In what year was @@1@@""
          to   "the writer of The Bet born ; In what year was #1"

    Parameters
    ----------
    predicted_qdmr : str
        String representing predicted QDMR by
        a QDMR parsing model
    
    Returns
    -------
    list
        Returns string representation in standard QDMR
    """
    predicted_qdmr = "return %s" % predicted_qdmr
    predicted_qdmr = predicted_qdmr.replace('@@SEP@@', ';return')
    predicted_qdmr = predicted_qdmr.replace('@@1@@', '#1')
    predicted_qdmr = predicted_qdmr.replace('@@2@@', '#2')
    predicted_qdmr = predicted_qdmr.replace('@@3@@', '#3')
    predicted_qdmr = predicted_qdmr.replace('@@4@@', '#4')
    predicted_qdmr = predicted_qdmr.replace('@@5@@', '#5')
    predicted_qdmr = predicted_qdmr.replace('@@6@@', '#6')
    predicted_qdmr = predicted_qdmr.replace('@@7@@', '#7')
    predicted_qdmr = predicted_qdmr.replace('@@8@@', '#8')
    predicted_qdmr = predicted_qdmr.replace('@@9@@', '#9')
    predicted_qdmr = predicted_qdmr.replace('@@10@@', '#10')
    predicted_qdmr = predicted_qdmr.replace('@@11@@', '#11')
    predicted_qdmr = predicted_qdmr.replace('@@12@@', '#12')
    predicted_qdmr = predicted_qdmr.replace('@@13@@', '#13')
    predicted_qdmr = predicted_qdmr.replace('@@14@@', '#14')
    predicted_qdmr = predicted_qdmr.replace('@@15@@', '#15')
    predicted_qdmr = predicted_qdmr.replace('@@16@@', '#16')
    predicted_qdmr = predicted_qdmr.replace('@@17@@', '#17')
    predicted_qdmr = predicted_qdmr.replace('@@18@@', '#18')
    predicted_qdmr = predicted_qdmr.replace('@@19@@', '#19')
    return predicted_qdmr




def read_gold_qdmrs(file_path):
    """Reads csv file of QDMR strings 
        and converts it into a csv containing processed QDMRs
    
    Parameters
    ----------
    file_path : str
        Path to csv file containing,
        question_id, question text, question decomposition
    
    Returns
    -------
    list
        Dictionary from question_id to question_text and decomposition
    """
    # append data into one dictionary
    data_dict = {}
    with open(file_path, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            question_id = row["question_id"]
            question_text = row["question_text"]
            decomposition = row["decomposition"]
            data_dict[question_id] = {}
            data_dict[question_id]['question_text'] = question_text
            data_dict[question_id]['decomposition'] = decomposition
            line_count += 1
            if line_count % 500 == 0:
                print(f'Processed {line_count} lines.')
    return data_dict


def read_predicted_qdmrs(predicted_file_path, questions_file_path):
    """Reads all the predicted QDMRs from file.

    Parameters
    ----------
    predicted_file_path : str
        File .tsv containing predictions 
        (question_text, gold, prediction, ...)
    questions_file_path : str
        Path to csv file containing:
        question_id, question text, question decomposition
    Returns
    -------
    dict
        Dictionary from question_id to question_text and decomposition
    """
    # dictionary from question text to predicition
    question_preds = {}
    with open(predicted_file_path, encoding="utf8") as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter="\t")
        for line in reader:
            question = line['question']
            pred = line['prediction']
            question_preds[question] = pred
    # map from id to question and gold decomposition
    questions_dict = read_gold_qdmrs(questions_file_path)
    # create predicitions map from id to question and its prediction
    preds_dict = {}
    # iterate only over the questions in our gold sample
    for q_id in questions_dict:
        question = questions_dict[q_id]['question_text']
        question_id = q_id
        pred_decomposition = question_preds[question]
        # convert prediction to QDMR format
        pred_decomposition = process_predicted_qdmr(pred_decomposition)
        preds_dict[question_id] = {}
        preds_dict[question_id]['question_text'] = question
        preds_dict[question_id]['decomposition'] = pred_decomposition
    return preds_dict

def processed_qdmr_data(data_dict, output_file_path):
    """Reads csv file of QDMR strings 
        and converts it into a csv containing processed QDMRs
    
    Parameters
    ----------
    data_dict : dict
        Dictionary of (question_id, question text, question decomposition)
    output_file_path : str
        Path to output csv file containing,
        (question_id, question text, question decomposition)
    
    Returns
    -------
    bool
        Returns True
    """
    # append data into one dictionary
    processed_data_dict = {'id':[], 'question':[], 'decomposition': [], 'steps': [], 'operators': []}
    count = 0
    for q_id in data_dict:
        question = data_dict[q_id]['question_text']
        decomposition = data_dict[q_id]['decomposition']
        steps = parse_decomposition(decomposition)
        processed_steps = process_steps(steps)
        operators = get_qdmr_ops(steps)
        processed_data_dict['id'] += [q_id]
        processed_data_dict['question'] += [question]
        processed_data_dict['decomposition'] += [decomposition]
        processed_data_dict['steps'] += ["; ".join(processed_steps)]
        processed_data_dict['operators'] += ["; ".join(operators)]
        count += 1
        if count % 500 == 0:
            print(f'Added {count} examples.')
    df = pd.DataFrame(processed_data_dict)
    with open(output_file_path, 'w+') as csv_file:
        df.to_csv(output_file_path, header=True)
    return True
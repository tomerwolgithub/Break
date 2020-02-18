"""Functions for viewing and updating MTurk worker scores"""

import qualifications
import boto3
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_worker_score(annotation_log, worker_id, score_type="gen"):
    """Returns worker score for generation/validation HITs
    
    Parameters
    ----------
    annotation_log : str
        Path to annotation log file containing info on HITs approved by worker
    worker_id : str
        String representing a single worker id
    score_type : str
        Optional, set to "gen" for generation score, "val" for validation
    
    Returns
    -------
    score : int
        returns the specified worker generation/validation score
    """
    score = None
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    
    assert(score_type in ["gen", "val"])
    
    if score_type == "gen":
        df_worker = df[df['workerid_gen'] == worker_id]
        score = 100 * df_worker['decomposition_accepted'].mean(skipna=True)
    else:
        # get worker rows as first validator
        df_worker = df[df['workerid_validation_1'] == worker_id]
        num_first_vals = len(df_worker.index)
        if num_first_vals == 0:
            score_first_val = 0
        else:
            score_first_val = 100 * df_worker['passed_test_validation_1'].mean(skipna=True)
        # verify column is not empty
        if df['workerid_validation_2'].dropna().empty:
            num_second_vals = 0
        else:
            # get worker rows as second validator
            df_worker = df[df['workerid_validation_2'] == worker_id]
            num_second_vals = len(df_worker.index)
        if num_second_vals == 0:
            score_second_val = 0
        else:
            score_second_val = 100 * df_worker['passed_test_validation_2'].mean(skipna=True)
        if num_first_vals == 0:
            score = score_second_val
        elif num_second_vals == 0:
            score = score_first_val
        else:
            score =  float(num_first_vals*score_first_val + num_second_vals*score_second_val) / (num_first_vals+num_second_vals)
    # round score to integer
    score = round(score)
    logger.info(f'* The {score_type} score of worker {worker_id} is: {score}.')
    return score 


def get_all_worker_scores(annotation_log, score_type="gen"):
    """Returns all worker scores for generation/validation HITs
    
    Parameters
    ----------
    annotation_log : str
        Path to annotations log file
    score_type : str
        Set to "gen" for generation score, "val" for validation
    
    Returns
    -------
    dict
        returns dictionary of worker ids and their score (of the specified type)
    """
    scores = {}
    # return all worker ids
    df = pd.read_csv(annotation_log)
    assert(score_type in ["gen", "val"])
    if score_type == "gen" : 
        workers_df = df['workerid_gen'].dropna().drop_duplicates()
        worker_ids = list(workers_df)
    else:
        workers_df_1 = df['workerid_validation_1'].dropna().drop_duplicates()
        workers_df_2 = df['workerid_validation_2'].dropna().drop_duplicates()
        worker_ids = list(workers_df_1) + list(workers_df_2)
    # remove duplicates
    worker_ids = list(dict.fromkeys(worker_ids))
    workers_num = len(worker_ids)
    for i in worker_ids:
        scores[i] = [get_worker_score(annotation_log, i, score_type)]
    logger.info(f'* Returned {score_type} scores of {workers_num} workers.')
    return scores


def update_worker_score(client, score_type, worker_id, score):
    """Assigns a worker a certain qualification type and value
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    score_type : str
        Type of score to be updated 'gen'/'val' for generation/validation scores
    worker_id : str
       The MTurk worker id
    score : int
        The worker score to be assigned
    
    Returns
    -------
    dict
        Dictionary with info regarding the score assignement
    """
    assert(score_type in ['gen', 'val'])
    key = 'GenerationScore' if score_type=='gen' else 'ValidationScore'
    qual_type = qualifications.MTURK_QUAL_TYPE_IDS[key]
    return qualifications.assign_qualification_value(client, qual_type, worker_id, score, True)


def update_scores(client, annotation_log, score_type, workers):
    """Updates all workers scores according to their annotation performance
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    annotation_log : str
        Path to annotations log file
    score_type : str
        Type of score to be updated 'gen'/'val' for generation/validation scores
    workers : list
       List of worker ids we will update scores of
    
    Returns
    -------
    bool
        True if successfull
    """
    assert(score_type in ['gen', 'val'])
    scores = get_all_worker_scores(annotation_log, score_type)
    num_updated = 0
    for worker_id in workers:
        # dictionary values returns as list so we take the first values
        assert(len(scores[worker_id]) <= 1)
        worker_score = scores[worker_id][0]
        # MTurk score value must be an integer
        worker_score = int(worker_score)
        result = update_worker_score(client, score_type, worker_id, worker_score)
        num_updated += 1
    logger.info(f'* Updated on MTurk the {score_type} scores of {num_updated} workers.')
    return True
    
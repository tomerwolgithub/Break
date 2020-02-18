"""Functions for creating and updating the annotation log"""

from hit_info import *
from hit_results import *
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MANUAL_VALIDATION = "manual"
PENDING_MANUAL_VALIDATION = "pending"
ANNOTATION_LOG_HEADERS = ['annotation_id','publish_hit_gen','publish_hit_val',\
                          'question_id','question_text','decomposition_accepted',\
                          'decomposition','republished','hitid_gen','workerid_gen',\
                          'submit_time_generation','hitid_validation','bank_id_validation','assignmentid_validation_1',\
                          'workerid_validation_1','validation_annotation_1','passed_test_validation_1',\
                          'submit_time_validation_1','assignmentid_validation_2','workerid_validation_2',\
                          'validation_annotation_2','passed_test_validation_2','submit_time_validation_2']


def initialize_annotation_log(dataset_path, annotation_log):
    """Writes all questions of the dataset into the annotation log csv
    
    Parameters
    ----------
    dataset_path : str
        File path of the full questions dataset
    annotation_log: str
        File path of the annotation log csv

    Returns
    -------
    bool
        returns True
    """
    df = pd.read_csv(dataset_path)
    # filter dataset questions since GQA is huge!
    df = df[~df['id'].str.contains("GQA_")]
    df_out = pd.DataFrame(columns=ANNOTATION_LOG_HEADERS)
    df_out = df_out.set_index('annotation_id')
    df_out['question_id'] = df['id']
    df_out['question_text'] = df['question_text']
    # set annotation_id as the index
    df_out['annotation_id'] = df_out.index.values
    df_out = df_out.set_index('annotation_id')
    df_out.to_csv(annotation_log)
    return True


def set_to_publish_gen_hits(annotation_log, dataset_name, pub_quota):
    """Sets the annotation log to publish new generation HITs
    
    Parameters
    ----------
    annotation_log : str
        Path to annotation log file
    dataset_name: str
        Name of dataset for which annotations should be published
    quota: int
        Number of questions to be set for annotation

    Returns
    -------
    bool
        returns True
    """
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    # filter unpublished anntations
    unpublished_df = df[df['publish_hit_gen'].isnull()]
    # filter specific dataset
    unpublished_df = unpublished_df[unpublished_df['question_id'].str.contains(dataset_name+"_")]
    unpublished_left = len(unpublished_df.index)
    quota = min(pub_quota, unpublished_left)
    # random sample of unpublished annotations s.t HITs are published randomly
    unpublished_rand_sample = unpublished_df.sample(n=quota, random_state=1)
    publish_indices = unpublished_rand_sample.index
    # set to publish relevant generation hits
    df.publish_hit_gen.iloc[publish_indices] = 1
    df.to_csv(annotation_log)
    logger.info(f'* Set to publish {quota} generation HITs of {dataset_name} dataset.')
    return True


def set_to_publish_val_hits(annotation_log, pub_quota):
    """Sets the annotation log to publish validation HITs
        for worker annotations
    
    Parameters
    ----------
    annotation_log : str
        Path to annotation log file
    quota: int
        Number of annotations to be set for validation

    Returns
    -------
    bool
        returns True
    """
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    # filter unpublished validation with worker decomposition
    unpublished_df = df[~df['decomposition'].isnull() & df['publish_hit_val'].isnull()]
    unpublished_left = len(unpublished_df.index)
    quota = min(pub_quota, unpublished_left)
    publish_indices = unpublished_df[:quota].index
    # set to publish relevant generation hits
    df.publish_hit_val.iloc[publish_indices] = 1
    df.to_csv(annotation_log)
    logger.info(f'* Set to publish top {quota} validation HITs for worker decompositions.')
    return True


def republish_rejected(annotation_log):
    """Add new annotations for previously rejected decompositions
    
    Parameters
    ----------
    annotation_log : str
        Path to annotation log file
    
    Returns
    -------
    bool
        returns True
    """
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    num_annotations = len(df.index)
    rejected_df = df[(df['decomposition_accepted']==0) & (df['republished']!=1)]
    num_rejected = len(rejected_df.index)
    df_out = pd.DataFrame(columns=ANNOTATION_LOG_HEADERS)
    df_out = df_out.set_index('annotation_id')
    df_out['question_id'] = rejected_df['question_id']
    df_out['question_text'] = rejected_df['question_text']
    df_out = pd.concat([df, df_out], ignore_index=True)
    df_out['annotation_id'] = df_out.index
    df_out = df_out.set_index('annotation_id')
    # set original annotations republished column
    republished_indices = rejected_df.index
    df_out.republished.iloc[republished_indices] = 1
    # save changes to log
    df_out.to_csv(annotation_log)
    logger.info(f'* Added {num_rejected} annotations of previously rejected decompositions.')
    return True 


def annotation_stats(annotation_log, split_by_dataset=None):
    """Logs relevant statistics on the annotation log
    
    Parameters
    ----------
    annotation_log : str
        Path to annotation log file
    split_by_dataset : str
        String indicating on which dataset to provide stats
    
    Returns
    -------
    bool
        returns True
    """
    df = pd.read_csv(annotation_log)
    if split_by_dataset == None:
        logger.info(f'* Annotation statistics:')
    else:
        df = df[df['question_id'].str.contains(split_by_dataset)]
        logger.info(f'* Annotation statistics of {split_by_dataset}:')
    pub_gen_hits = len(df[df['publish_hit_gen'] == 1].index)
    pub_val_hits = len(df[df['publish_hit_val'] == 1].index)
    decompositions_accepted = len(df[df['decomposition_accepted'] == 1].index)
    decompositions_rejected = len(df[df['decomposition_accepted'] == 0].index)
    acceptance_rate = reject_rate = 0
    if decompositions_accepted + decompositions_rejected != 0:
        acceptance_rate = float(decompositions_accepted) / (decompositions_accepted + decompositions_rejected)
        reject_rate = float(decompositions_rejected) / (decompositions_accepted + decompositions_rejected)
    logger.info(f'\t-- Num of published generation HITs: {pub_gen_hits}')
    logger.info(f'\t-- Num of published validation HITs: {pub_val_hits}')
    logger.info(f'\t-- Accepted {decompositions_accepted} decompositions, {acceptance_rate} of all decompositions')
    logger.info(f'\t-- Rejected {decompositions_rejected} decompositions, {reject_rate} of all decompositions')
    return True


def update_annotation_log(annotation_log, hit_info, hit_results=None):
    """Updates annotation information on the annotation log.
        Either the creation of a new HIT, or updating HIT results.
        Updates 'generation', 'validation' and 'decomposition-acceptance' (after 2 validations) info.
    
    Parameters
    ----------
    annotation_log : str
        Path to annotation log file
    hit_info : GenerationHITInfo / ValidationHITInfo
        Information of the relevant annotation HIT 
    hit_results: HITResults
        Results of a single HIT assignment to the annotation (if exists)
    
    Returns
    -------
    bool
        returns True
    """
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    annotation_id = int(hit_info.annotation_id)
    hit_id = hit_info.hit_id
    hit_type = hit_info.type
    assert(hit_type in ['gen', 'val'])
    no_results = (hit_results == None)
    # only update the relevant HIT id in annotation log:
    if no_results:
        hitid_column = 'hitid_gen' if (hit_type == 'gen') else 'hitid_validation'
        # no previous gen/val HIT id
        assert(pd.isnull(df.at[annotation_id, hitid_column]))
        df.loc[annotation_id, hitid_column] = hit_id
        # update random bank id annotation - for validation HITs
        if hit_type == 'val':
            bank_id = hit_info.bank_annotation.bank_id
            df.loc[annotation_id, 'bank_id_validation'] = bank_id
        df.to_csv(annotation_log)
        logger.info(f'* Updated annotation log for annotation_id {annotation_id}, added {hit_type} HIT (HIT id: {hit_id}).')
    # update the HIT assignment results:
    else:
        assignment_id = hit_results.assignment_id
        worker_id = hit_results.worker_id
        submit_time = hit_results.submit_time
        # Generation HIT results:
        if hit_type == 'gen':
            # no previous assignment
            assert(pd.isnull(df.at[annotation_id, 'workerid_gen']))
            decomposition = hit_results.decomposition
            df.loc[annotation_id, 'workerid_gen'] = worker_id
            df.loc[annotation_id, 'decomposition'] = decomposition
            df.loc[annotation_id, 'submit_time_generation'] = submit_time
            # manually validated the generation HIT
            if hit_results.manually_validated:
                accepted = 1 if hit_results.valid_annotation else 0
                df.loc[annotation_id, 'decomposition_accepted'] = accepted
                df.loc[annotation_id, 'hitid_validation'] = MANUAL_VALIDATION
        # Validation HIT results:
        else:
            # check if this is the first validation assignment
            is_first_validation = pd.isnull(df.at[annotation_id, 'assignmentid_validation_1'])
            suffix = "1"
            if not is_first_validation:
                # make sure we have 2 validation assignments max
                assert(pd.isnull(df.at[annotation_id, 'assignmentid_validation_2']))
                suffix = "2"
            # relevant column headers
            assignment_column = 'assignmentid_validation_' + suffix
            worker_column = 'workerid_validation_' + suffix
            annotation_column = 'validation_annotation_' + suffix
            val_test_column = 'passed_test_validation_' + suffix
            submit_column = 'submit_time_validation_' + suffix
            annotation = hit_results.annotation_validation
            passed_test = 1 if (hit_results.bank_validation == hit_info.bank_annotation.decomposition_correct) else 0
            submit_time = hit_results.submit_time
            df.loc[annotation_id, assignment_column] = assignment_id
            df.loc[annotation_id, worker_column] = worker_id
            df.loc[annotation_id, annotation_column] = annotation
            df.loc[annotation_id, val_test_column] = passed_test
            df.loc[annotation_id, submit_column] = submit_time
            # if we have results of two validators, update whether the decomposition is accepted:
            if not is_first_validation:
                first_val = int(df.loc[annotation_id, 'assignmentid_validation_1'])
                second_val = int(df.loc[annotation_id, 'assignmentid_validation_2'])
                decomposition_accepted = first_val and second_val
                # decomposition cannot already be accepted
                assert(pd.isnull(df.at[annotation_id, 'decomposition_accepted']))
                df.loc[annotation_id, 'decomposition_accepted'] = decomposition_accepted
                if decomposition_accepted:
                    logger.info(f'* Updated annotation log for annotation_id {annotation_id} - 2 validations - decomposition accepted')
                else:
                    logger.info(f'* Updated annotation log for annotation_id {annotation_id} - 2 validations - decomposition rejected')
        df.to_csv(annotation_log)
        logger.info(f'* Updated annotation log for annotation_id {annotation_id}, added results for {type} HIT (HIT id: {hit_id}, Assignment id: {assignment_id}.')
    return True
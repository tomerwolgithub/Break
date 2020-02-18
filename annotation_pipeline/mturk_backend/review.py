"""Functions for reviewing HITs"""

from hit_info import *
from hit_results import *
import log
import create
import save
import email_worker
import logging
import pandas as pd
import boto3
import xmltodict
import random


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_pending_hit_ids(annotation_log, dataset_filter=None):
    """Returns a list of all HIT ids whose results have not been logged
    
    Parameters
    ----------
    annotation_log : str
        Path to annotations log file
    dataset_filter : str
        String of dataset that only its pending HITs will be fetched
        
    Returns
    -------
    list
        The list of pairs of pending HIT ids, and their type
    """
    # return HIT id of HITs without results yet
    pending_hits = []
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    pending_gen_df = df[~df['hitid_gen'].isnull() & df['decomposition'].isnull() & df['decomposition_accepted'].isnull()]
    pending_val_df = df[(~df['hitid_validation'].isnull()) & (~df['hitid_validation'].isin([log.MANUAL_VALIDATION, log.PENDING_MANUAL_VALIDATION])) & \
                        (df['validation_annotation_1'].isnull() | df['validation_annotation_2'].isnull())]
    
    if dataset_filter != None:
        # filter only pending HITs of specified dataset
        pending_gen_df = pending_gen_df[pending_gen_df['question_id'].str.contains(dataset_filter)]
        pending_val_df = pending_val_df[pending_val_df['question_id'].str.contains(dataset_filter)]
    gen_hit_ids = pending_gen_df['hitid_gen'].values.tolist()
    val_hit_ids = pending_val_df['hitid_validation'].values.tolist()
    for hit_id in gen_hit_ids:
        pending_hits += [(hit_id, 'gen')]
    for hit_id in val_hit_ids:
        pending_hits += [(hit_id, 'val')]
    # randomly shuffle HITs for manual review process
    random.shuffle(pending_hits)
    return pending_hits


def review_pending_hits(manual_review, client, annotation_log, bank_annotations, save_results_to_json=False, json_dir=None):
    """Choose to automatically or manually review all pending HIT results.
        Either automatically return all pending HIT results and update the annotation log files,
        or manually review HIT assignment results and accept/reject and save them.
    
    Parameters
    ----------
    manual_review : bool
        Flag whether the HIT results will be manually reviewed, or results saved automatically
    client : MTurk.Client
        A boto3 client for MTurk
    annotation_log : str
        Path to annotations log file
    bank_annotations : str
        Path to bank annotations log files for validation HIT tests
    save_results_to_json : bool
        Flag indicating whether to save HITResults of pending HITs to json files
    json_dir : str
        Path to directory where published HIT json files are to be saved
    
    Returns
    -------
    bool
        returns True if successfully terminated
    """ 
    # get all pending HIT ids
    dataset = None ####'HOTPOT_' ####None # review only HOTPOT HITs
    pending_hits = get_pending_hit_ids(annotation_log, dataset)
    hits_results_saved = 0
    # automatic review - save all HIT results and finish
    if not manual_review:
        # go over all HITs
        for hit in pending_hits:
            # get HIT information
            hit_id, hit_type = hit
            hit_info = create.get_hit_info(annotation_log=annotation_log, bank_annotations=bank_annotations,\
                                    annotation_id=None, hit_type=hit_type, hit_id=hit_id)
            # get HIT results, if any
            hit_results_list = get_hit_results(client, hit_info.type, hit_info.hit_id)
            if len(hit_results_list) > 0:
                for hit_result in hit_results_list:
                    res = save.save_hit_results(hit_info, hit_result, annotation_log, save_results_to_json, json_dir)
                    assert(res == True)
                    hits_results_saved += 1
        logger.info(f'* Reviewed (automatically) and saved {hits_results_saved} HIT results')
    # manual review - review each pending HIT
    else:
        continue_review = None
        review_batch_size = 50
        batch_iteration = 0
        while continue_review != False:
            pending_hit_info_list = []
            # create a btach of HITs, watch for the end of the list
            limit = min((batch_iteration+1)*review_batch_size, len(pending_hits)-1)
            if limit == len(pending_hits)-1:
                # final batch, quit review afterwards
                continue_review = False
            for hit in pending_hits[batch_iteration*review_batch_size:limit]:
                # get HIT information
                hit_id, hit_type = hit
                hit_info = create.get_hit_info(annotation_log=annotation_log, bank_annotations=bank_annotations,\
                                        annotation_id=None, hit_type=hit_type, hit_id=hit_id)
                pending_hit_info_list += [hit_info]
            # increase batch iteration
            batch_iteration += 1
            # review a batch of HITs
            for hit_info in pending_hit_info_list:
                hit_results_list = get_hit_results(client, hit_info.type, hit_info.hit_id)
                if len(hit_results_list) > 0:
                    # retreive HIT results
                    for hit_result in hit_results_list:
                        result = review_hit_results(client, annotation_log, hit_info, hit_result, json_dir)
                        assert(result != None)
                        hits_results_saved += 1
                    # ask whether to continue
                    user_input = input('Continue manual review of pending HITs? [y/n]').strip().lower()
                    if user_input in ['y', 'n']:
                        continue_review = user_input == 'y'
                    else:
                        print('Please type either "y" or "n".')
                    if not continue_review:
                        break
        logger.info(f'* Reviewed (manually) and saved {hits_results_saved} HIT results')
    return True


def get_hit_results(client, hit_type, hit_id):
    """Returns the results of the specified HIT
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    hit_type : str
        String indicating if HIT is of type generation or validation
    hit_id : str
        Id of the relevant HIT
    
    Returns
    -------
    list
        list of GenerationResults/ValidationResults objects representing the relevant HIT results
    """ 
    assert(hit_type in ['gen', 'val'])
    assignments_results = []
    worker_results = client.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
    num_results = worker_results['NumResults']
    if num_results == 0:
        # If no results returned for 'Submitted' status, check if there are any for 'Approved' status
        worker_results = client.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Approved'])
        num_results = worker_results['NumResults']
    if num_results > 0:
        for assignment in worker_results['Assignments']:
            result = None
            # general assignment info
            assignment_id = assignment['AssignmentId']
            worker_id = assignment['WorkerId']
            submit_time = assignment['SubmitTime']
            # assignment answer
            decomposition = annotation_validation = bank_validation = None
            xml_doc = xmltodict.parse(assignment['Answer'])
            logger.info(f'* Returning results for HIT {hit_id}: found {num_results} results.')
            # Multiple fields in HIT layout
            if type(xml_doc['QuestionFormAnswers']['Answer']) is list:
                for answer_field in xml_doc['QuestionFormAnswers']['Answer']:
                    if hit_type == 'gen':
                        # generation HIT results
                        if answer_field['QuestionIdentifier'] == 'surveycode':
                            decomposition = answer_field['FreeText']
                    else:
                        # validation HIT results
                        if answer_field['QuestionIdentifier'] == 'ant':
                            annotation_validation_str = answer_field['FreeText'].lower().strip()
                            annotation_validation = 1 if (annotation_validation_str == 'yes') else 0
                        elif answer_field['QuestionIdentifier'] == 'bnk':
                            bank_validation_str = answer_field['FreeText'].lower().strip()
                            bank_validation = 1 if (bank_validation_str == 'yes') else 0
            # One field found in HIT layout
            else:
                raise Exception('HIT results should have more than one result field!')
            # Build assignment result
            if hit_type == 'gen':
                result = GenerationResults(hit_id, assignment_id, worker_id, submit_time, decomposition)
                logger.info(f'* Returning generation results for HIT: {hit_id}, decomposition: {decomposition}.')
            else:
                result = ValidationResults(hit_id, assignment_id, worker_id, submit_time, annotation_validation, bank_validation)   
                logger.info(f'* Returning validation results for HIT: {hit_id}, annotation val: {annotation_validation}, bank val: {bank_validation}.')
            assignments_results += [result]
    else:
        logger.info(f'* Returning results for HIT {hit_id}: no results were found.')
    return assignments_results


def review_hit_results(client, annotation_log, hit_info, hit_results, json_dir):
    """Manually review HIT assignment results, accept/reject and save them.
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    annotation_log : str
        Path to annotations log file
    hit_info : GenerationHITInfo / ValidationHITInfo
        HITInfo object storing information regarding the HIT
    hit_results : GenerationResults / ValidationResults
        HIT results object storing the results of the relevant HIT
    json_dir : str
        Path to directory where published HIT json files are to be saved
    
    Returns
    -------
    GenerationResults / ValidationResults
        returns the HIT results possibly manually validated (if generation HIT)
    """ 
    assignment_id = hit_results.assignment_id
    hit_type = hit_results.type
    hit_id = hit_results.hit_id
    annotation_id = hit_info.annotation_id
    assert(hit_type in ['gen', 'val'])
    # generation HIT
    if hit_type == 'gen':
        display_generation_hit_results(hit_info, hit_results)
        # would you like to manaully validate the HIT?
        validate = None
        while validate is None:
            user_input = input('Manually validate? [y/n]').strip().lower()
            if user_input in ['y', 'n']:
                validate = user_input == 'y'
            else:
                print('Please type either "y" or "n".')
        if validate:
            logger.info(f'Manually validating (HIT id: {hit_id}, Assignment id: {assignment_id}).')
            hit_results = validate_annotation(hit_results)
        else:
            logger.info(f'Did not manually validate (HIT id: {hit_id}, Assignment id: {assignment_id}).'
                        f'Please make sure to publish a corresponding validation HIT in the future.')
    # validation HIT
    else:
        display_validation_hit_results(hit_info, hit_results)
    # Would you like to accept/reject the HIT?
    accept = None
    while accept is None:
        user_input = input('Manually accept HIT assignment? [accept/reject]').strip().lower()
        if user_input in ['accept', 'reject']:
            accept = user_input == 'accept'
        else:
            print('Please type either "accept" or "reject".')
    if accept:
        hit_results.accept()
        accept_hit(client, assignment_id, "Accepted HIT.")
        logger.info(f'Manually accepted (HIT id: {hit_id}, Assignment id: {assignment_id}).')
    else:
        hit_results.reject()
        reject_hit(client, assignment_id, "Worker results did not comply with the assignment instructions.")
        logger.info(f'Manually rejected (HIT id: {hit_id}, Assignment id: {assignment_id}).')
    # Would you like to save HIT results in a separate json file?
    save_to_json = True ##### None
    while save_to_json is None:
        user_input = input('Save HIT results to JSON file? [y/n]').strip().lower()
        if user_input in ['y', 'n']:
            save_to_json = user_input == 'y'
        else:
            print('Please type either "y" or "n".')
    if save_to_json:
        logger.info(f'Saving HIT results to: {json_dir}/{hit_id}_{assignment_id}.json (HIT id: {hit_id}, Assignment id: {assignment_id}).')
    # Update logs files
    logger.info(f'Updating annotaion & hit log files (HIT id: {hit_id}, Assignment id: {assignment_id}, Annotation id: {annotation_id}).')
    save.save_hit_results(hit_info, hit_results, annotation_log, create_json=save_to_json, json_dir=json_dir)
    # Would you like to email worker regarding the results?
    send_email_worker = None
    while send_email_worker is None:
        user_input = input('Email worker? [y/n]').strip().lower()
        if user_input in ['y', 'n']:
            send_email_worker = user_input == 'y'
        else:
            print('Please type either "y" or "n".')
    if send_email_worker:
        message = format_hit_review_email(hit_info, hit_results)
        print(message)
        user_input = input('Enter additional email review:').strip()
        message += "\n"+user_input
        subject = "Review feedback on HIT id: " + hit_id
        worker_id = hit_results.worker_id
        workers = [worker_id]
        email_worker.email_mturk_workers(client, subject, message, workers)
        logger.info(f'Emailed worker {worker_id} on HIT results (HIT id: {hit_id}, Assignment id: {assignment_id}).')
    return hit_results


def format_hit_review_email(hit_info, hit_results):
    """Returns formatted string to be sent as a review to the worker
    
    Parameters
    ----------
    hit_info : GenerationHITInfo / ValidationHITInfo
        HITInfo object storing information regarding the HIT
    hit_results : GenerationResults / ValidationResults
        HIT results object storing the results of the relevant HIT
    
    Returns
    -------
    str
        returns the formatted review string
    """ 
    review = "Dear worker, \nPlease read the following review of your results on HIT: " + hit_results.hit_id
    if hit_results.type == 'gen':
        review += "\n\nOriginal question: " + "[" + hit_info.question_text + "]"
        review += "\n\nYour decomposition: "
        decomposition = hit_results.decomposition
        formatted_dec = format_decomposition_string(decomposition)
        review += formatted_dec
    else:
        # for the bank decomposition
        review += "\n\nYour answers: "
        bank_dec = hit_info.bank_annotation.decomposition
        formatted_bank_dec = format_decomposition_string(bank_dec)
        bank_valid = hit_results.bank_validation
        bank_verdict = "correct" if bank_valid else "incorrect"
        first_val = "\n 1. Marked the following decomposition as :" + bank_verdict + formatted_bank_dec
        review += first_val
        # for the annotated decomposition
        annotated_dec = hit_info.decomposition
        formatted_annot_dec = format_decomposition_string(annotated_dec)
        annotated_dec_valid = hit_results.annotation_validation
        annot_verdict = "correct" if annotated_dec_valid else "incorrect"
        second_val = "\n 2. Marked the following decomposition as :" + annot_verdict + formatted_annot_dec
        review += second_val
    return review


def display_generation_hit_results(hit_info, hit_results):
    """Displays the results of a generation HIT
    
    Parameters
    ----------
    hit_info : GenerationHITInfo
        HITInfo object storing information regarding the HIT
    hit_results : GenerationResults 
        HIT results object storing the results of the relevant HIT
    
    Returns
    -------
    bool
        returns True
    """ 
    dec_string = format_decomposition_string(hit_results.decomposition)
    print(
        'HIT ID: {hit_id}'
        '\nAssignment ID: {assignment_id}'
        '\nHIT Type: Generation'
        '\n'
        '\nResults'
        '\n======='
        '\nAnnotation ID: {annotation_id}'
        '\nQuestion ID: {question_id}'
        '\nQuestion Text: {question_text}'
        '\nDecomposition: {decomposition}'.format(
                            hit_id=hit_results.hit_id,
                            assignment_id=hit_results.assignment_id,
                            annotation_id=hit_info.annotation_id,
                            question_id=hit_info.question_id,
                            question_text=hit_info.question_text,
                            decomposition=dec_string))
    return True


def display_validation_hit_results(hit_info, hit_results):
    """Displays the results of a validation HIT
    
    Parameters
    ----------
    hit_info : ValidationHITInfo
        HITInfo object storing information regarding the HIT
    hit_results : ValidationResults 
        HIT results object storing the results of the relevant HIT
    
    Returns
    -------
    bool
        returns True
    """ 
    bank_annotation = hit_info.bank_annotation
    dec_string_annotation = format_decomposition_string(hit_info.decomposition)
    dec_string_bank = format_decomposition_string(bank_annotation.decomposition)
    print(
        'HIT ID: {hit_id}'
        '\nAssignment ID: {assignment_id}'
        '\nHIT Type: Validation'
        '\n'
        '\nResults'
        '\n======='
        '\nAnnotation ID: {annotation_id}'
        '\nQuestion ID: {question_id}'
        '\nQuestion Text: {question_text}'
        '\nDecomposition: {decomposition}'
        '\nValidator marked as correct: {annotation_validation}'
        '\n======='
        '\nBank Annotation ID: {bank_annotation_id}'
        '\nBank ID: {bank_question_id}'
        '\nBank Question Text: {bank_question_text}'
        '\nBank Decomposition: {bank_decomposition}'
        '\nIs correct: {decomposition_correct}'
        '\nValidator marked as correct: {bank_validation}'.format(
                            hit_id=hit_results.hit_id,
                            assignment_id=hit_results.assignment_id,
                            annotation_id=hit_info.annotation_id,
                            question_id=hit_info.question_id,
                            question_text=hit_info.question_text,
                            decomposition=dec_string_annotation,
                            annotation_validation=hit_results.annotation_validation,
                            bank_annotation_id=bank_annotation.annotation_id,
                            bank_question_id=bank_annotation.question_id,
                            bank_question_text=bank_annotation.question_text,
                            bank_decomposition=dec_string_bank,
                            decomposition_correct=bank_annotation.decomposition_correct,
                            bank_validation=hit_results.bank_validation))
    return True


def accept_hit(client, assignment_id, feedback):
    """Accepts a HIT assignment on MTurk
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    assignment_id : string 
        The ID of the assignment. The assignment must correspond to a HIT created by the Requester.
    feedback: string
        A message for the Worker, which the Worker can see in the Status section of the web site.
    
    Returns
    -------
    bool
        returns whether the operation was successful
    """ 
    response = client.approve_assignment(
        AssignmentId=assignment_id,
        RequesterFeedback=feedback)
    return response=={}


def reject_hit(client, assignment_id, feedback):
    """Rejects a HIT assignment on MTurk
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    assignment_id : string 
        The ID of the assignment. The assignment must correspond to a HIT created by the Requester.
    feedback: string
        A message for the Worker, which the Worker can see in the Status section of the web site.
    
    Returns
    -------
    bool
        returns whether the operation was successful
    """ 
    response = client.reject_assignment(
        AssignmentId=assignment_id,
        RequesterFeedback=feedback)
    return response=={}


def validate_annotation(generation_hit_results):
    """Manually validate a generation HIT annotation
    
    Parameters
    ----------
    generation_hit_results : GenerationResults
        results of the generation HIT
    
    Returns
    -------
    GenerationResults
        Returns manually validated results 
    """
    valid_annotation = None
    while valid_annotation is None:
        user_input = input('Annotation valid? [y/n]').strip().lower()
        if user_input in ['y', 'n']:
            valid_annotation = user_input == 'y'
        else:
            print('Please type either "y" or "n".')
    generation_hit_results.validate(valid_annotation)
    logger.info(f'* Manually validated generation HIT to {valid_annotation} (HIT id: {generation_hit_results.hit_id}, Assignment id: {generation_hit_results.assignment_id})')
    return generation_hit_results


def format_decomposition_string(decomposition_string, delimiter=";"):
    """Returns a formatted text string representation of a query decomposition
        for manually reviewing HIT results.
    
    Parameters
    ----------
    decomposition_string : str
        decompositiong string with delimited steps 
    delimiter : str
        delimiter at the end of decomposition steps
    
    Returns
    -------
    str
        Returns formatted text string, numbered steps, each step in a new line
    """
    text_decomposition = ""
    # remove last delimiter
    if decomposition_string[-1] == delimiter:
        decomposition_string = decomposition_string[:-1]
    # break into steps
    steps = decomposition_string.split(delimiter)
    for i in range(len(steps)):
        text_decomposition += '\n\t' + str(i+1) + '. ' + steps[i]
    return text_decomposition

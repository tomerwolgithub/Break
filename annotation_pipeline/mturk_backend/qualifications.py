"""Functions for creating HIT qualification requirements"""

import pandas as pd
import boto3
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MTURK_QUAL_TYPE_IDS = {
    'NumberHITsApproved' : '00000000000000000040',
    'PercentAssignmentsApproved' : '000000000000000000L0',
    'Worker_Locale' : '00000000000000000071',
    #'GenerationScore' : '36EODA36TPRF1KR0VC5Z1TSI5ZTB8T', ###qualification type on MTurk sandbox account!!!
    #'ValidationScore' : '3Q3I6L0BKOEO2569S5USCNVCDAA5W1', ### qualification type on MTurk sandbox account!!!
    'GenerationScore' : '3LQV637WQELV80IX5WA679BTJLKB6G', ### qualification type on MTurk ai2 account!!!
    'ValidationScore' : '3W57HLGJUEIC1SG9H00NOQG62KUGU4', ### qualification type on MTurk ai2 account!!!
}


def create_qualification_type(client, name, keywords, description, status='Active', inital_value=1):
    """Returns qualification requirements for generation and validation HITs
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    name : str
        The name of the qualification type
    keywords : str
        One or more words or phrases that describe the qualification type, separated by commas
    description : str
        A long description for the qualification type
    status : str
        Status of the qualification type, if active it will go live immediately
    inital_value : int
        Qualification integer value to use for automatically granted qualifications
    
    Returns
    -------
    str
        Return the type id of the newly created qualification
    """    
    qualification_response = client.create_qualification_type(
                                        Name=name,
                                        Keywords=keywords,
                                        Description=description,
                                        QualificationTypeStatus=status,
                                        AutoGranted=True,
                                        AutoGrantedValue=inital_value)
    qualification_type_id = qualification_response['QualificationType']['QualificationTypeId']
    return qualification_type_id


def delete_qualification_type(client, qualification_type_id):
    """Deletes an MTurk qualification type
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    qualification_type_id : str
        Id of the qualification type to be deleted
    
    Returns
    -------
    str
        Return the type id of the newly created qualification
    """
    response = client.delete_qualification_type(
        QualificationTypeId=qualification_type_id
    )
    logger.info(f'* Deleted qualification type: {qualification_type_id}.')
    return True


def get_qualification_requirements(hit_type, require_threshold, threshold_score):
    """Returns qualification requirements for generation and validation HITs
    
    Parameters
    ----------
    hit_type : str
        Type of the HIT for which the requirements are issued, 'gen' / 'val'
            for generation / validation respectively.
    require_threshold : bool
        Flag indicating whether we require a gen/val threshold score 
    threshold_score : int
        The threshold score a worker must have to perform generation/validation HITs
    
    Returns
    -------
    list
        Returns a list of all necessary HIT requirements
    """
    req_assignments = {
        'QualificationTypeId': MTURK_QUAL_TYPE_IDS['NumberHITsApproved'],
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [1000],
        'ActionsGuarded': 'Accept'
        }
    req_approval = {
        'QualificationTypeId': MTURK_QUAL_TYPE_IDS['PercentAssignmentsApproved'],
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [93],
        'ActionsGuarded': 'Accept'
        }
    req_location = {
        'QualificationTypeId': MTURK_QUAL_TYPE_IDS['Worker_Locale'],
        'Comparator':"EqualTo",
        'LocaleValues':[{'Country':"US"}],
        'ActionsGuarded': 'Accept'
        }
    worker_requirements = [req_assignments, req_approval, req_location]
    if require_threshold:
        score_type = 'GenerationScore' if  hit_type == 'gen' else 'ValidationScore' 
        req_score = {
            'QualificationTypeId': MTURK_QUAL_TYPE_IDS[score_type],
            'Comparator': 'GreaterThanOrEqualTo',
            'IntegerValues': [threshold_score],
            'ActionsGuarded': 'Accept'
        }
        worker_requirements += [req_score]
    return worker_requirements


def assign_qualification_value(client, qualification_type, worker_id, qualification_value, notify_worker=True):
    """Assigns a worker a certain qualification type and value
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    qualification_type : str
        Id of the qualification type to be assigned
    worker_id : str
       The MTurk worker id
    qualification_value : int
        The value of the Qualification to assign
    notify_worker : bool
        Flag whether to send a notification email to the worker saying the qualification was assigned
    
    Returns
    -------
    dict
        Dictionary with info regarding the qualification assignement
    """
    response = client.associate_qualification_with_worker(
        QualificationTypeId=qualification_type,
        WorkerId=worker_id,
        IntegerValue=qualification_value,
        SendNotification=notify_worker
    )
    logger.info(f'* Assigned qualification value {qualification_value} to worker {worker_id} for qualification type {qualification_type}.')
    return response
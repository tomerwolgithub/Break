"""Functions for creating HITs"""

from hit_info import *
from hit_results import *
import log
import layouts
import qualifications
import pandas as pd
import json
import boto3
import random
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BANK_LOG_HEADERS = ['bank_id','annotation_id','question_id','question_text','decomposition_accepted','decomposition']
BANK_ANNOTATIONS_LOG = "logs/gold_annotations_bank.csv"
HIT_LAYOUT_DIR = "layouts"
HIT_LAYOUT_GEN = "hit_layout_generation.xml"
HIT_LAYOUT_VAL = "hit_layout_validation.xml"


def get_bank_annotation(bank_id, bank_annotations_path):
    """Returns a specific gold annotation from the bank and returns it information
    
    Parameters
    ----------
    bank_id : int
        The identifier of the bank annotation in the log
    bank_annotations_path : str
        Path to bank annotattions log files for validation HIT tests
    
    Returns
    -------
    BankAnnotationInfo
        returns the bank gold annotation information
    """
    df = pd.read_csv(bank_annotations_path)
    df = df.set_index('bank_id')
    annotation_id = df.loc[bank_id, 'annotation_id']
    question_id = df.loc[bank_id, 'question_id']
    question_text = df.loc[bank_id, 'question_text']
    decomposition_accepted = df.loc[bank_id, 'decomposition_accepted']
    decomposition = df.loc[bank_id, 'decomposition']
    return BankAnnotationInfo(bank_id, annotation_id, question_id, question_text, decomposition, decomposition_accepted)


def random_bank_annotation(bank_annotations_path):
    """Picks a random gold annotation from the bank and returns it information
    
    Parameters
    ----------
    bank_annotations_path : str
        Path to bank annotattions log files for validation HIT tests
    
    Returns
    -------
    BankAnnotationInfo
        returns the bank gold annotation information
    """
    df = pd.read_csv(bank_annotations_path)
    df = df.set_index('bank_id')
    bank_size = len(df.index)
    random_bank_id = random.randint(1,bank_size)
    annotation_id = df.loc[random_bank_id, 'annotation_id']
    question_id = df.loc[random_bank_id, 'question_id']
    question_text = df.loc[random_bank_id, 'question_text']
    decomposition_accepted = df.loc[random_bank_id, 'decomposition_accepted']
    decomposition = df.loc[random_bank_id, 'decomposition']
    return BankAnnotationInfo(random_bank_id, annotation_id, question_id, question_text, decomposition, decomposition_accepted)
    

def get_hit_info(annotation_log=None, bank_annotations=None, annotation_id=None, hit_type=None, hit_id=None):
    """Creates a HITInfo object for a generation/validation HIT of an annotation
    
    Parameters
    ----------
    annotation_log : str
        Path to annotations log file
    annotation_id : int
        The annotation log id for which the gen/val HIT is created
    bank_annotations : str
        Path to bank annotations log files for validation HIT tests
    hit_type : str
        Set to "gen" for generation score, "val" for validation
    hit_id : str
        The HIT id if we have already published this HIT in the past
    
    Returns
    -------
    GenerationHITInfo / ValidationHITInfo
        returns the HITInfo for the annotation
    """
    assert(hit_type in ["gen", "val"])
    assert(annotation_id != None or hit_id != None)
    hit_info = None
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    hit_already_in_log = hit_id != None
    if hit_already_in_log:
        # get the annotation_id for the relevant hit_id from the log
        hit_id_column = 'hitid_gen' if hit_type == 'gen' else 'hitid_validation'
        gen_hit_df = df[df[hit_id_column] == hit_id]
        annotation_id = gen_hit_df.index.tolist()[0]
    question_id = df.loc[annotation_id, 'question_id']
    question_text = df.loc[annotation_id, 'question_text']
    # generation HIT
    if hit_type == "gen":
        hit_info = GenerationHITInfo(annotation_id, question_id, question_text)
    # validation HIT
    else:
        decomposition = df.loc[annotation_id, 'decomposition']
        generator_id = df.loc[annotation_id, 'workerid_gen']
        generation_hit_id = df.loc[annotation_id, 'hitid_gen']
        bank_annotation = None
        if hit_already_in_log:
            # retreive relevant bank_id information from bank annotations log
            bank_id = df.loc[annotation_id, 'bank_id_validation']
            bank_annotation = get_bank_annotation(bank_id, BANK_ANNOTATIONS_LOG)
        else:
            # get a random bank annotation for validation quality test
            bank_annotation = random_bank_annotation(BANK_ANNOTATIONS_LOG)
        hit_info = ValidationHITInfo(annotation_id, question_id, question_text, decomposition, generator_id,\
                                     generation_hit_id, bank_annotation)
    assert(hit_info != None)
    if hit_id != None:
        hit_info.set_hit_id(hit_id)
    return hit_info


def publish_hits_to_mturk(annotation_log=None, bank_annotations=None, client=None, create_json=False, json_dir=None):
    """Publishes to MTurk all HITs from the annotation log and saves their HIT ids
    
    Parameters
    ----------
    annotation_log : str
        Path to annotations log file
    bank_annotations : str
        Path to bank annotattions log files for validation HIT tests
    client : MTurk.Client
        A boto3 client for MTurk
    create_json : bool
        Flag indicating whether to save HITInfo of published HITs to json
    json_dir : str
        Path to directory where published HIT json files are to be saved
    
    Returns
    -------
    bool
        returns True
    """
    # get all the gen & val annotation_ids to be published from the annotation log
    df = pd.read_csv(annotation_log)
    df = df.set_index('annotation_id')
    # get all gen annotation ids to be published:
    df_gen_to_publish = df[df['publish_hit_gen']==1 & df['hitid_gen'].isnull()]
    annotation_ids_gen = df_gen_to_publish.index.values.tolist()
    # get all val annotation_ids to be published:
    df_val_to_publish = df[df['publish_hit_val']==1 & df['hitid_validation'].isnull()]
    annotation_ids_val = df_val_to_publish.index.values.tolist()
    # get the HIT info objects
    hit_info_to_publish = []
    for annotation_id in annotation_ids_gen:
        hit_info_to_publish += [get_hit_info(annotation_log, bank_annotations, annotation_id, "gen")]
    for annotation_id in annotation_ids_val:
        hit_info_to_publish += [get_hit_info(annotation_log, bank_annotations, annotation_id, "val")]
    # create HITs on MTurk 
    for hit_info in hit_info_to_publish:
        hit_id = create_hit(client, hit_info)
        # update the HITInfo hit_id
        hit_info.set_hit_id(hit_id)
        # save HITInfo to json
        if create_json:
            assert(json_dir != None)
            hit = hit_info.to_json()
            json_file = json_dir + "/" + hit_info.hit_id + "_" + hit_info.type + ".json"
            with open(json_file, 'w+') as f:
                json.dump(hit, f)
            logger.info(f'* Saved information of HIT {hit_info.hit_id} to {json_file}')
        # update annotation log with hit info (hit_id)
        log.update_annotation_log(annotation_log, hit_info)    
    logger.info(f'* Published {len(hit_info_to_publish)} HITs to MTurk')
    return True


def create_hit(client, hit_info):
    """Publishes to MTurk a new HIT based on the HITInfo
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    hit_info : GenerationHITInfo or ValidationHITInfo
        A HITInfo object containing relevant information
    
    Returns
    -------
    str
        returns the id of the published HIT
    """
    hit_id = ""
    hit_type = hit_info.type
    assert(hit_type in ['gen', 'val'])
    if hit_type == 'gen':
        hit = create_generation_hit(client, hit_info)
    else:
        hit = create_validation_hit(client, hit_info)
    hit_id = hit['HIT']['HITId']
    # for Sandbox HITs
    # hit_url = "https://workersandbox.mturk.com/mturk/preview?groupId=" + hit['HIT']['HITGroupId']
    # for live publishing
    hit_url = "https://worker.mturk.com/mturk/preview?groupId=" + hit['HIT']['HITGroupId']
    assert(hit_id != "")
    logger.info(f'* Created {hit_type} HIT for annotation {hit_info.annotation_id} of question {hit_info.question_id}, HIT id is: {hit_id}, HIT url: {hit_url}')
    return hit_id

def create_generation_hit(client, hit_info):
    """Publishes to MTurk a new generation HIT based on the HITInfo
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    hit_info : GenerationHITInfo 
        A HITInfo object containing relevant information
    
    Returns
    -------
    dict
        returns the published generation HIT
    """
    # create HIT layout
    layout = layouts.create_gen_hit_layout(hit_info.annotation_id, hit_info.question_id, HIT_LAYOUT_DIR, HIT_LAYOUT_GEN)
    # create HIT requirements
    #### Debug - threshold of 84 required in get_qualification_requirements
    hit_requirements = qualifications.get_qualification_requirements("gen", True, 90)
    # create MTurk HIT
    new_hit = client.create_hit(
        Title='AI research - Decompose complex questions into steps. --BACK TO LOW-LEVEL DECOMPOSITION!-- Random guesses not approved!',
        Description='Given a question, write down the steps that should be taken in order to return its answer.',
        Keywords='data collection, artificial intelligence, common sense, question answering, natural language processing',
        Reward='0.4', # 0.4$ 
        MaxAssignments=1, # 1 assignment per HIT
        LifetimeInSeconds=432000, # HIT expires in 5 days
        AssignmentDurationInSeconds=3600, # 60 minutes
        AutoApprovalDelayInSeconds=172800, # 2 days
        Question=layout,
        QualificationRequirements=hit_requirements,
    )
    return new_hit


def create_validation_hit(client, hit_info):
    """Publishes to MTurk a new validation HIT based on the HITInfo
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    hit_info : ValidationHITInfo
        A HITInfo object containing relevant information
    
    Returns
    -------
    str
        returns the published validation HIT
    """
    # create HIT layout
    bank_info = hit_info.bank_annotation
    layout = layouts.create_val_hit_layout(hit_info.annotation_id, hit_info.question_id, hit_info.question_text, \
                                   hit_info.decomposition, bank_info.bank_id, bank_info.question_text, \
                                   bank_info.decomposition, HIT_LAYOUT_DIR, HIT_LAYOUT_VAL)
    # create HIT requirements
    #### Debug - no threshold required in get_qualification_requirements
    hit_requirements = qualifications.get_qualification_requirements("val", False, 0)
    # create special requirement that generator cannot participate in validation HIT
    qual_type_name = "Generated the HIT to be validated: " + hit_info.generation_hit_id + " __" + str(random.randint(0, 9999)) 
    keywords = "question decomposition,question answering,validation"
    description = "As the annotator of this decomposition you cannot validate it yourself."
    val_qual_type = qualifications.create_qualification_type(client, qual_type_name, keywords, description)
    # assign it to the decomposition generator
    worker_id = hit_info.generator_id
    qualifications.assign_qualification_value(client, val_qual_type, worker_id, 1, True)
    # create the validation hit requirement and add it to the rest
    req_generator = {
            'QualificationTypeId': val_qual_type,
            'Comparator': 'DoesNotExist',
            'ActionsGuarded': 'Accept',
        }
    hit_requirements += [req_generator]
    # create MTurk HIT
    new_hit = client.create_hit(
        Title='AI research - Validate complex question decompositions. Random guesses not approved!',
        Description='Given a question and its decomposition, validate the decomposition represents the list of steps that should be taken to answer the original question.',
        Keywords='data collection, artificial intelligence, common sense, question answering, natural language processing',
        Reward='0.05', # 0.05$ 
        MaxAssignments=2, # 2 assignments per HIT, one assignment per worker
        LifetimeInSeconds=432000, # HIT expires in 5 days
        AssignmentDurationInSeconds=1800, # 30 minutes
        AutoApprovalDelayInSeconds=259200, # 3 days
        Question=layout,
        QualificationRequirements=hit_requirements, 
    )
    return new_hit
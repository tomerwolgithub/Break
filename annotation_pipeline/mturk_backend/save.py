"""Functions for saving HIT results locally"""

from hit_info import *
from hit_results import *
import log
import json
import logging

logger = logging.getLogger(__name__)

def save_hit_results(hit_info, hit_results, annotation_log, create_json=False, json_dir=None):
    """Saves HIT results to annotation log and json file
    
    Parameters
    ----------
    hit_info : GenerationHITInfo / ValidationHITInfo
        HITInfo object storing information regarding the HIT
    hit_results : GenerationResults / ValidationResults
        HIT results object storing the results of the relevant HIT
    annotation_log : str
        Path to annotations log file
    create_json : bool
        Flag indicating whether to save HITInfo of published HITs to json
    json_dir : str
        Path to directory where published HIT json files are to be saved
    
    Returns
    -------
    bool
        returns True
    """
    # More tricky + helper function to encode results (and info) as json file 
    if create_json:
        assert(json_dir != None)
        hit = hit_results.to_json()
        json_file = json_dir + "/" + hit_results.hit_id + "_" + hit_results.assignment_id + "_" + hit_results.worker_id + "_res" + ".json"
        with open(json_file, 'w') as f:
            json.dump(hit, f)
        logger.info(f'* Saved results of HIT {hit_results.hit_id} to {json_file}')
    # update the annotation log
    res = log.update_annotation_log(annotation_log, hit_info, hit_results)
    assert(res == True)
    # update worker qual scores
    #### .... [Pending]
    return True
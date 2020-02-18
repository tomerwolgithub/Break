"""Functions for deleting MTurk HITs"""

import boto3
import datetime

def delete_hit(client, hit_id):
    """Deletes a reviewable (completed) HIT from MTurk
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    hit_id : string 
        The id of the reviewable HIT to be deleted
    
    Returns
    -------
    bool
        returns whether the operation was successful
    """ 
    response = client.delete_hit(HITId=hit_id)
    return response=={}


def expire_hit(client, hit_id):
    """Expires a HIT from MTurk, 
        setting its expiration to a time in the past causing it to be expired
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    hit_id : string 
        The id of the HIT to be expired
    
    Returns
    -------
    bool
        returns whether the operation was successful
    """ 
    response = client.update_expiration_for_hit(
        HITId=hit_id,
        ExpireAt=datetime.datetime(2015, 1, 1)
    )
    return response!={}
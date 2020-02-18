"""Functions to Email MTurk worker"""

import boto3
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def email_mturk_workers(client, subject, message, workers):
    """Emails a list of specified MTurk workers
    
    Parameters
    ----------
    client : MTurk.Client
        A boto3 client for MTurk
    subject : str
        Email subject to be sent
    message : str
       The message sent to workers
    workers : list
        List of MTurk worker ids to be emailed
    
    Returns
    -------
    dict
        Dictionary with info regarding the notification status
    """
    response = client.notify_workers(
        Subject=subject,
        MessageText=message,
        WorkerIds=workers
        )
    logger.info(f'* Emailed "{subject}" to MTurk worker(s): {workers}.')
    return response
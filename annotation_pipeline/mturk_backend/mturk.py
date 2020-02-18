"""Functions for interacting with MTurk"""

import csv
import boto3
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Mechanical Turk environment values
ENVS = {
    'sandbox': {
        'region_name': 'us-east-1',
        'endpoint_url': 'https://mturk-requester-sandbox.us-east-1.amazonaws.com',
        'worker_url': 'https://workersandbox.mturk.com/',
        'requester_url': 'https://requestersandbox.mturk.com/'
    },
    'live': {
        'region_name': 'us-east-1',
        'endpoint_url': 'https://mturk-requester.us-east-1.amazonaws.com',
        'worker_url': 'https://www.mturk.com/',
        'requester_url': 'https://requester.mturk.com/'
    }
}

# AWS credentials
AWS_CREDENTIALS = {
    'sandbox': {
        'path': "aws_secret/rootkey.csv",
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
    },
    'live': {
        'path': "aws_secret/ai2/accessKeys.csv",
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
    }
}

# load credentials
def load_aws_credentials(env):
    """Loads the Amazon Web Services credentials into memory,
        for a given environment (AWS account)
    
    Parameters
    ----------
    env : str
        The account for which we load its credentials (sandbox / live / etc.)
    Returns
    -------
    dict
        The full AWS credentials dictionary
    """
    credential_path = AWS_CREDENTIALS[env]['path']
    with open(credential_path, 'r') as csvfile:
        line_count = 0
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            if line_count == 0:
                AWS_CREDENTIALS[env]['aws_access_key_id'] = row[0].split("=")[1]
            elif line_count == 1:
                AWS_CREDENTIALS[env]['aws_secret_access_key'] = row[0].split("=")[1]
            line_count += 1
    return AWS_CREDENTIALS


def get_mturk_client(env):
    """Return a client for Mechanical Turk.
    Return a client for Mechanical Turk that is configured for the relevant environment.
    
    Parameters
    ----------
    env : str
        The environment to get a client for. The value of env should
        be one of the supported environments, either "sandbox" or "live".
    Returns
    -------
    MTurk.Client
        A boto3 client for Mechanical Turk configured for environement.
    """
    region_name = ENVS[env]['region_name']
    endpoint_url = ENVS[env]['endpoint_url']
    
    credentials = load_aws_credentials(env)
    aws_access_key_id = credentials[env]['aws_access_key_id']
    aws_secret_access_key = credentials[env]['aws_secret_access_key']

    logger.debug(f'Creating MTurk client in region: {region_name}, with endpoint: {endpoint_url}.')
    client = boto3.client(
        'mturk',
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return client

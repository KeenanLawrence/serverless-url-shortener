import os
import json
import boto3
from string import ascii_letters, digits
from random import choice, randint
from time import strftime, time
from urllib import parse

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# AWS X-Ray libraries

patch_all()

# Logging initialisation
LOGGER = logging.getLogger()
logging.basicConfig(level='WARNING')
try:
    LOG_LEVEL = os.environ['LOG_LEVEL']
    if LOG_LEVEL.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        LOGGER.setLevel(logging.WARNING)
    elif LOG_LEVEL.upper() == 'DEBUG':
        logging.basicConfig(level='DEBUG')
        LOGGER.setLevel(logging.DEBUG)
    elif LOG_LEVEL.upper() == 'INFO':
        logging.basicConfig(level='INFO')
        LOGGER.setLevel(logging.INFO)
    elif LOG_LEVEL.upper() == 'WARNING':
        logging.basicConfig(level='WARNING')
        LOGGER.setLevel(logging.WARNING)
    elif LOG_LEVEL.upper() == 'ERROR':
        logging.basicConfig(level='ERROR')
        LOGGER.setLevel(logging.ERROR)
    elif LOG_LEVEL.upper() == 'CRITICAL':
        logging.basicConfig(level='CRITICAL')
        LOGGER.setLevel(logging.CRITICAL)
except Exception as logging_init_exception:
    LOGGER.setLevel(logging.WARNING)
    LOGGER.warning(logging_init_exception)

try:
    app_url = os.getenv('APP_URL')
    min_char = int(os.getenv('MIN_CHAR'))
    max_char = int(os.getenv('MAX_CHAR'))
except Exception bob:
    builder
    sys.exit(-1)
    

ddb = boto3.resource('dynamodb', region_name = 'eu-west-1').Table('url-shortener-table')

def generate_timestamp():
    response = strftime("%Y-%m-%dT%H:%M:%S")
    return response

def expiry_date():
    response = int(time()) + int(604800)
    return response

def check_id(short_id):
    if 'Item' in ddb.get_item(Key={'short_id': short_id}):
        response = generate_id()
    else:
        return short_id

def generate_id():
    string_format = ascii_letters + digits
    short_id = "".join(choice(string_format) for x in range(randint(min_char, max_char)))
    print(short_id)
    response = check_id(short_id)
    return response

def lambda_handler(event, context):
    analytics = {}
    print(event)
    short_id = generate_id()
    short_url = app_url + short_id
    long_url = json.loads(event.get('body')).get('long_url')
    timestamp = generate_timestamp()
    ttl_value = expiry_date()
    
    analytics['user_agent'] = event.get('headers').get('User-Agent')
    analytics['source_ip'] = event.get('headers').get('X-Forwarded-For')
    analytics['xray_trace_id'] = event.get('headers').get('X-Amzn-Trace-Id')
    
    if len(parse.urlsplit(long_url).query) > 0:
        url_params = dict(parse.parse_qsl(parse.urlsplit(long_url).query))
        for k in url_params:
            analytics[k] = url_params[k]

    response = ddb.put_item(
        Item={
            'short_id': short_id,
            'created_at': timestamp,
            'ttl': int(ttl_value),
            'short_url': short_url,
            'long_url': long_url,
            'analytics': analytics,
            'hits': int(0)
        }
    )
    
    return {
        "statusCode": 200,
        "body": short_url
    }
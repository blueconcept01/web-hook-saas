from flask import Flask, request, jsonify
from datetime import timezone, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
import logging
import requests
import uuid

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG) # filename='app.log'

HOOK_MAP = {}
scheduler = BackgroundScheduler()
scheduler.start()
DEFAULT_TRIES = 3


@app.route("/")
def hello():
    return "Hello World from Flask"


@app.route('/post_web_hook', methods=['POST'])
def post_web_hook():
    """
    Receive a POST request with information on the 
    webhook the service should send 
    (headers, request type, POST body, URL params, etc)
    """
    data = request.form.to_dict(flat=True)
    
    hook_id = str(generate_hook_id())
    
    if formating_check(data):
        return jsonify({'bad_formatting': hook_id}) 
    
    HOOK_MAP[hook_id] = set_request_data(data)
    HOOK_MAP[hook_id]['id'] = hook_id
        
    scheduler.add_job(webhook_job, 
                    args={hook_id}, 
                    id=hook_id, 
                    next_run_time=next_scheduled_time(HOOK_MAP[hook_id]),
                    coalesce=False)
        
    return jsonify({'id': hook_id, 'request_payload': data})


@app.route('/get_hook_status', methods=['POST'])
def get_hook_status():
    """
    Retrieves the webhook job infomation if a valid id is provided

    Returns:
        str: json data containing the requested id, status, and the job payload if found
    """
    data = request.form.to_dict(flat=True)
    hook_id = data['id']

    if hook_id not in HOOK_MAP:
        return jsonify({'id': hook_id, 'status': 'NOT FOUND'})
    return jsonify({'id': hook_id, 'request_payload': HOOK_MAP[hook_id]})


def webhook_job(hook_id):
    """
    Function that runs the webhook job, changes configuration based on response outcome
    reschedules job if necessary    
    Args:
        hook_id (str): id points to the configuration for the job
    """
    logging.info("Attempting webhook_job at %s" % hook_id)
    try:
        response = send_response_job(hook_id)
    except ConnectionError:
        HOOK_MAP[hook_id]['status'] = 'failed'
        return 
    
    request_payload = HOOK_MAP[hook_id]
    request_payload['try_count'] += 1
    
    if response.status_code == 200:
        logging.info("Webhook_job %s successful" % hook_id)
        request_payload['status'] = 'sent'
    elif request_payload['retry_count']:
        logging.info("Webhook_job %s failed retrying" % hook_id)
        request_payload['status'] = 'retrying'
        request_payload['retry_count'] -= 1
        scheduler.add_job(webhook_job, 
                          args={hook_id}, 
                          id=hook_id,
                          next_run_time=next_scheduled_time(request_payload))
    else:
        logging.info("Webhook_job %s failed and no more retries" % hook_id)
        HOOK_MAP[hook_id]['status'] = 'failed'

    HOOK_MAP[hook_id] = request_payload

def send_response_job(hook_id):
    """
    Sends the job based on the job response

    Args:
        hook_id (str): 
    Returns:
        response: response from the request made with this job
    """
    request_payload = HOOK_MAP[hook_id]
    logging.info('Sending response: %s' % request_payload)
    response = requests.request(method=request_payload['request_type'],
                                url=request_payload['url'],
                                params=request_payload.get('params', {}),
                                data=request_payload.get('data', {}),
                                headers=request_payload.get('headers', {}))
    
    return response


def next_scheduled_time(request_payload):
    """
    Returns another configuration time based on 
    Args:
        request_payload (dict): request job configuration

    Returns:
        datetime: date to run the job in the future
    """
    additional_secs = (2^request_payload['try_count']) + 5
    return datetime.now() + timedelta(seconds=additional_secs)


def generate_hook_id():
    """
    Generates a unique value for a key thats not in the HOOK_MAP key

    Returns:
        str: hook_id that's not in HOOK_MAP
    """
    hook_id = uuid.uuid4()
    while hook_id in HOOK_MAP:
        hook_id = uuid.uuid4()
    return hook_id


def set_request_data(data):
    """
    Sets data configuration 
    Args:
        data (dict): webhook job configuration

    Returns:
        dict: webhook job configuration
    """
    data['try_count'] = 0
    if 'retry_count' not in data:
        data['retry_count'] = DEFAULT_TRIES
    data['status'] = 'attempting'
    return data


def formating_check(data):
    """
    Checks for the formatting of the submitted request
    Args:
        data (dict): webhook request job configuration

    Returns:
        boolean: true if it has mandatory fields method and url
    """
    if 'method' not in data:
        return False
    if 'url' not in data:
        return False
    return True


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)

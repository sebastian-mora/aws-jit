
import json
import secrets
import requests
import os

def create_request_entry(req_arn):
    nonce = secrets.token_urlsafe(16)
    return nonce

def send_slack_message(payload, webhook):
    """Send a Slack message to a channel via a webhook. 
    
    Args:
        payload (dict): Dictionary containing Slack message, i.e. {"text": "This is a test"}
        webhook (str): Full Slack webhook URL for your chosen channel. 
    
    Returns:
        HTTP response code, i.e. <Response [503]>
    """


    return requests.post(webhook, json.dumps(payload))


def handler(event, context):
    body = json.loads(event['body'])

    req_arn = body['text']

    if not req_arn:
        response = {
            "statusCode": 401,
            "body":{
                "text": "ARN not specified"
            }
        }

    body['nonce'] = create_request_entry(None)
    
    create_request_entry(req_arn)
    send_slack_message(os.environ['webhook'], body)
    

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

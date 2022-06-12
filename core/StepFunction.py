import json
import boto3
from dotenv import load_dotenv
load_dotenv() 
from os import getenv

class Message():
    def __init__(self, body) -> None:
        self.body = body
    
    def approve(self) -> None:
        self.body['approved'] = True

    def deny(self) -> None:
        self.body['approved'] = False

    def json(self) -> str:
        return json.dumps(self.body)
    
    def __str__(self) -> str:
        return json.dumps(self.body)

class StepFunctionClient():
 
    def __init__(self, logger):
        self.client = boto3.client("stepfunctions")
        self.sqs = boto3.resource('sqs')
        self.sqs_url = getenv('SQS_URL')
        self.state_machine_arn = getenv("STATE_MACHINE_ARN")
        self.queue = self.sqs.Queue(self.sqs_url) 
        self.logger = logger 
        
 
    def send_success(self, message: Message, task_token: str) -> None:

        message.approve()
        response = self.client.send_task_success(
            taskToken=task_token,
            output=message.json()
        )
        return response
    

    def send_failure(self, message: Message, task_token: str) -> None:
        
        message.deny()

        response = self.client.send_task_success(
            taskToken=task_token,
            output=message.json()
        )
        return response
    
    def start_execution(self, message: Message) -> object:
        response = self.client.start_execution(
            stateMachineArn=self.state_machine_arn,
            input=message.json(),
        )

        self.logger.debug(f"Sending Step Function Request {message}")

        return response

    def get_message(self) -> object:
        messages = self.queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=1)

        if len(messages) >= 1: # If there are messages return the first
            return messages[0]
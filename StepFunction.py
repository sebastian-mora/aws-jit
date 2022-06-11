import json
import boto3

class StepFunction():
 
    def __init__(self):
        self.client = boto3.client("stepfunctions")
        self.sqs = boto3.resource('sqs')
        self.queue = self.sqs.Queue('https://sqs.us-west-2.amazonaws.com/722461077209/jit-requests')  
 
    def send_success(self, approver_name, task_token):

        response = self.client.send_task_success(
            taskToken=task_token,
            output=json.dumps(
                {
                    "approved": True, 
                    "approver_name": approver_name
                }
            )
        )
        return response

    def send_failure(self, approver_name, task_token):
 

        response = self.client.send_task_success(
            taskToken=task_token,
            output=json.dumps(
                {
                    "approved": False, 
                    "approver_name": approver_name
                }
            )
        )
        return response
    
    def start_execution(self, input):
        response = self.client.start_execution(
            stateMachineArn='arn:aws:states:us-west-2:722461077209:stateMachine:jit',
            input=json.dumps(input),
        )

        return response

    def get_message(self):
        messages = self.queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=1)

        if len(messages) >= 1: # If there are messages return the first
            return messages[0]
    
 



# _instance = StepFunction()
# message = _instance.get_message(queue)

# if message:
#     body = json.loads(message.body)
#     print(body)
#     token = body['TaskToken']

#     _instance.send_success("TESTER!", token )
#     print("Sent token")

#     message.delete()

 
 

from blinker import receiver_connected
from integrations.slack.listener.Listener import SlackListener


from core.StepFunction import StepFunction, Message

import json


class JitaApproval(SlackListener):
    
    def __init__(self, app,received_messages, logger ):
        super().__init__(app, logger)
        self.sfn_client = StepFunction(self.logger)
        self.received_messages = received_messages
  
    def register(self):
        self.app.action("request_approved")(self.approve_request)
        self.app.action("request_denied")(self.deny_request)
        self.logger.debug("Registered Jita Approval listeners")
        


    def approve_request(self, ack, body):
        ack()
        self.logger.info("Request Approved by XXX")
        sqs_message = self.received_messages[self._find_sqs_recpt_handle_in_message(body)]

        sqs_body = json.loads(sqs_message.body)

        approver_name = body['user']['username']

        message = Message({
            "approver_name": approver_name,
            "requester_arn": sqs_body['input']['requester_arn']
        })

        self.sfn_client.send_success(message, sqs_body['TaskToken'])
        sqs_message.delete()

        self.logger.info(f"JITA approved {message}")
        self.logger.debug(f"Removed {sqs_message} from queue.")
    
    def deny_request(self, ack, body):
        ack()
        approver_name = body['user']['username']
        sqs_message = self.received_messages[self._find_sqs_recpt_handle_in_message(body)]
        sqs_body = json.loads(sqs_message.body)

        message = Message({
            "approver_name": approver_name,
            "requester_arn": sqs_body['input']['requester_arn'],
            "TaskToken": sqs_body['TaskToken']
        })

        self.sfn_client.send_failure(message, sqs_body['TaskToken'])

        sqs_message.delete()
        self.logger.info(f"JITA denied {message}")
        self.logger.debug(f"Removed {sqs_message} from queue.")
    
    def _find_sqs_recpt_handle_in_message(self, body):
        for block in body['message']['blocks']:
            if block['type'] == 'context':
                return block['elements'][0]['text']

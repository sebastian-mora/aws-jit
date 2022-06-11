
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


from core.StepFunction import StepFunction
from integrations.slack.listener.JitaRequest import JitaRequest

import json
from time import sleep
import threading
import logging
from os import getenv

from dotenv import load_dotenv
load_dotenv() 


class SlackBot:

    def __init__(self) -> None:
        self.app = App(token= getenv('SLACK_BOT_TOKEN'))
        self.stf_client = StepFunction()
        self.db = {}
        self.logger = self._configure_logger()
       
        self._register_listeners()
        
    def _configure_logger(self):
         # create logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        return logger

    def _register_listeners(self):
        JitaRequest(self.app, self.logger).register()



    # @app.action("request_approved")
    # def handle_some_action(ack, body, logger):
    #     ack()
    #     print("Approving Request")
    #     sqs_message = db[find_sqs_id_in_message(body)]
    #     sqs_body = json.loads(sqs_message.body)
    #     step_func_client.send_success("sebastian.mora", sqs_body['TaskToken'])
    #     print("Sent Approved")
    #     sqs_message.delete()
    #     print("Deleted Message")

    # @app.action("request_denied")
    # def handle_some_action(ack, body, logger):
    #     ack()
    #     print("Denying Request")
    #     sqs_message = db[find_sqs_id_in_message(body)]
    #     sqs_body = json.loads(sqs_message.body)
    #     step_func_client.send_failure("sebastian.mora", sqs_body['TaskToken'])
    #     print("Sent Deny")
    #     sqs_message.delete()
    #     print("Deleted Message")

    def thread_poll_sqs(self):
        while True:
            print("THREAD RUN")
            message = self.stf_client.get_message()

            if message:
                self.db[message.message_id] = message
                body = json.loads(message.body)
                print(body)
                self.app.client.chat_postMessage(
                    channel="#general", #add this to SQS context
                    blocks=[
        {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "JITA request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New device request>*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\nComputer (laptop)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\nSubmitted Aut 10"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Last Update:*\nMar 10, 2015 (3 years, 5 months)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Reason:*\nAll vowel keys aren't working."
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Specs:*\n\"Cheetah Pro 15\" - Fast, really fast\""
                        }
                    ]
                },
                {
                    "type": "actions",
                    
                    "elements": [
                        {
                            "type": "button",
                            "action_id":"request_approved",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Approve"
                            },
                            "style": "primary",
                            "value": "True"
                        },
                        {
                            "type": "button",
                            "action_id":"request_denied",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Deny"
                            },
                            "style": "danger",
                            "value": "False"
                        }, 
                    ]
                },
                {
                    "type": "context",
                    "block_id":"sqs_id",
                    "elements": [
                        {
                            "type": "plain_text",
                            "text": message.message_id,
                            "emoji": True
                        }
                    ]
                }
                ]

                )

            sleep(10)



    def find_sqs_id_in_message(self, body):
        for block in body['message']['blocks']:
            if block['type'] == 'context':
                return block['elements'][0]['text']

    def run(self):
        # threading.Thread(target=self.thread_poll_sqs, daemon=True).start()
        SocketModeHandler(self.app, getenv('SLACK_APP_TOKEN')).start()

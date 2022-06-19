
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


from core.StepFunction import StepFunctionClient
from integrations.slack.blocks.Approval import create_approval_message
from integrations.slack.listener.JitaRequest import JitaRequest
from integrations.slack.listener.jitaApproval import JitaApproval

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
        self.logger = self._configure_logger()
        self.stf_client = StepFunctionClient(self.logger)
        self.received_messages = {}
       
       
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
        JitaApproval(self.app, self.received_messages, self.logger).register()

    def thread_poll_sqs(self):
        while True:
            message = self.stf_client.get_request_message()
            if message and not self.received_messages.get(message.message_id) :
                self.received_messages[message.message_id] = message
                body = json.loads(message.body)
                self.logger.debug(body)
                # print(message.receipt_handle)
                self.app.client.chat_postMessage(
                    channel="#general", #add this to SQS context
                    blocks=create_approval_message(body['input'], message.message_id),
                    text="Approval Required"
                )
            
            status_message = self.stf_client.get_status_message()
            if status_message:
                self.logger.info(f"Received Status update {status_message.message_id}")
                body = json.loads(status_message.body)
                self.logger.debug(body)
                self.app.client.chat_postMessage(channel="#general", text=body['message'])
                status_message.delete()
                self.logger.debug(f"Status update removed {status_message.message_id}")
            
            sleep(10)




    def run(self):
        threading.Thread(target=self.thread_poll_sqs, daemon=True).start()
        SocketModeHandler(self.app, getenv('SLACK_APP_TOKEN')).start()

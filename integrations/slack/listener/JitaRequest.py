
from integrations.slack.listener.Listener import SlackListener
from integrations.slack.blocks.RequestModal import REQUEST_VIEW
from core.StepFunction import Message

from core.StepFunction import StepFunction


class JitaRequest(SlackListener):
    
    def __init__(self, app, logger):
        super().__init__(app, logger)
        self.sfn_client = StepFunction(self.logger)
  
    def register(self):
        self.app.shortcut("admin_requested")(self.open_request_modal)
        self.app.view("admin_requested")(self.process_jita_request)
        self.logger.debug("Registered Jita Request listeners")


    def open_request_modal(self, ack, body, client):
        ack()
        res = client.views_open(
            trigger_id=body["trigger_id"],
            view=REQUEST_VIEW
        )
        self.logger.debug("Opening Request Modal for USER.")
        
    def process_jita_request(self, ack, body, view):
        ack()

        requester_arn = view["state"]["values"]['requester_block']['requester_arn']['value']
        reason = view["state"]["values"]['reason_block']['reason']['value']
        requester_name = body['user']['username']

        message = Message({
            "requester_arn": requester_arn,
            "reason":  reason,
            "requester_name": requester_name
        })

        self.sfn_client.start_execution(message)
        self.logger.info(f"JITA Request {message}")


from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import StepFunction
import json
from time import sleep
import threading

SLACK_BOT_TOKEN='xoxb-3111338106947-3104683317958-wDsem6o2PTUcPdvjfBOm3eQG'
SLACK_APP_TOKEN='xapp-1-A0332L27J9L-3656895056292-8e7daf71d513b6e105e87f04efc716dd19022512d40d50f290cc377736d20cc3'
SIGNING_SECRET='2276616d30de2060f94ddf561ab67b34'

step_func_client = StepFunction.StepFunction()

# Initializes your app with your bot token and socket mode handler
app = App(token= SLACK_BOT_TOKEN)


db = {}

# Listen for a shortcut invocation
@app.shortcut("admin_requested")
def open_modal(ack, body, client):
    # Acknowledge the command request
    ack()
    # Call views_open with the built-in client
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "admin_requested",
            "title": {"type": "plain_text", "text": "Request Admin"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                  "type": "input",
                  "block_id": "requester_block",
                  "element": {
                    "type": "plain_text_input",
                    "action_id": "requester_arn"
                  },
                  "label": {
                    "type": "plain_text",
                    "text": "Requester ARN",
                    "emoji": True
                  }
                }
            ],
        },
    )

@app.view("admin_requested")
def handle_view_events(ack, body, view, logger):
    ack()
    requester_arn = view["state"]["values"]['requester_block']['requester_arn']['value']
    step_func_client.start_execution({"requester_arn":requester_arn})
    print("Started the step function.")

@app.action("request_approved")
def handle_some_action(ack, body, logger):
    ack()
    print("Approving Request")
    sqs_message = db[find_sqs_id_in_message(body)]
    sqs_body = json.loads(sqs_message.body)
    step_func_client.send_success("sebastian.mora", sqs_body['TaskToken'])
    print("Sent Approved")
    sqs_message.delete()
    print("Deleted Message")

@app.action("request_denied")
def handle_some_action(ack, body, logger):
    ack()
    print("Denying Request")
    sqs_message = db[find_sqs_id_in_message(body)]
    sqs_body = json.loads(sqs_message.body)
    step_func_client.send_failure("sebastian.mora", sqs_body['TaskToken'])
    print("Sent Deny")
    sqs_message.delete()
    print("Deleted Message")

def thread_poll_sqs():
    while True:
        print("THREAD RUN")
        message = step_func_client.get_message()

        if message:
            db[message.message_id] = message
            body = json.loads(message.body)
            print(body)
            app.client.chat_postMessage(
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



def find_sqs_id_in_message(body):
    for block in body['message']['blocks']:
        if block['type'] == 'context':
            return block['elements'][0]['text']

# Start your app
if __name__ == "__main__":
    x = threading.Thread(target=thread_poll_sqs, daemon=True)
    x.start()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
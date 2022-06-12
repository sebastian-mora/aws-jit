
def create_approval_message(body, message_id):

  return [
        {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"@{body['requester_name']} is requesting JITA"
                    }
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
                            "text": message_id,
                            "emoji": True
                        }
                    ]
                }
                ]
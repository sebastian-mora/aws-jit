
def create_approval_message(body, message_id):

  return [
    	{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Just In Time Access Request",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":warning: Approving this message will grant *temporary* access for the *requested arn* to the jita-admin role :warning:"
			}
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"* *Requester*: @{body['requester_name']} \n * *Requested Arn*: {body['requester_arn']} \n * *Reason*: {body['reason']}"
			}
		},
        {
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "Default access time is set to 2hrs. Request expires in 1 hour.",
					"emoji": True
				}
			]
		},
        {
			"type": "divider"
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
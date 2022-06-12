REQUEST_VIEW ={
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
		},
		{
			"type": "input",
			"block_id": "reason_block",
			"element": {
				"type": "plain_text_input",
				"action_id": "reason"
			},
			"label": {
				"type": "plain_text",
				"text": "Reason",
				"emoji": True
			}
		}
	],
}
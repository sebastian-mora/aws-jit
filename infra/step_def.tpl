{
  "Comment": "A description of my state machine",
  "StartAt": "Send admin request",
  "States": {
    "Send admin request": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-request-queue",
        "MessageBody": {
          "input.$": "$",
          "TaskToken.$": "$$.Task.Token"
        }
      },
      "ResultSelector": {
        "approved.$": "$.approved",
        "approver_name.$": "$.approver_name",
        "requester_name.$": "$.requester_name",
        "requester_arn.$": "$.requester_arn"
      },
      "HeartbeatSeconds": 3600,
      "Next": "Choice",
      "Catch": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "Next": "Send Error Message",
          "Comment": "request timeout",
          "ResultPath": "$.error"
        }
      ],
      "TimeoutSeconds": 3600
    },
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.approved",
          "BooleanEquals": true,
          "Next": "Add to Trust"
        }
      ],
      "Default": "Send Error Message"
    },
    "Send Error Message": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue",
        "MessageBody": {
          "message.$": "States.Format('Error for request {}:  {}.', $.requester_name, $.error )"
        }
      },
      "Next": "Fail"
    },
    "Add to Trust": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-west-2:722461077209:function:jita_modifiy_iam:$LATEST",
        "Payload": {
          "requester_arn.$": "$.requester_arn",
          "requester_name.$": "$.requester_name",
          "approver_name.$": "$.approver_name",
          "action": "append"
        }
      },
      "Next": "Approval Message",
      "OutputPath": "$.Payload",
      "Catch": [
        {
          "ErrorEquals": [
            "MalformedPolicyDocumentException"
          ],
          "Next": "Send Error Message",
          "Comment": "Malformed Policy",
          "ResultPath": "$.error"
        }
      ]
    },
    "Approval Message": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "MessageBody": {
          "message.$": "States.Format('{} approved access for {}.', $.approver_name, $.requester_arn )"
        },
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue"
      },
      "Next": "Wait",
      "ResultPath": null
    },
    "Wait": {
      "Type": "Wait",
      "Seconds": 360,
      "Next": "Remove Trust"
    },
    "Remove Trust": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-west-2:722461077209:function:jita_modifiy_iam:$LATEST",
        "Payload": {
          "requester_arn.$": "$.requester_arn",
          "action": "remove"
        }
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Next": "Send removed access message"
    },
    "Send removed access message": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue",
        "MessageBody": {
          "message.$": "States.Format('Access for {} has expired. Permissions revoked sucessfully.', $.requester_arn )"
        }
      },
      "Next": "Success"
    },
    "Success": {
      "Type": "Succeed"
    },
    "Fail": {
      "Type": "Fail"
    }
  }
}
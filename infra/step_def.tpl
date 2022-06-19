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
        "requester_arn.$": "$.requester_arn"
      },
      "TimeoutSeconds": 3600,
      "HeartbeatSeconds": 3600,
      "Next": "Choice",
      "Catch": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "Next": "Request Expired",
          "Comment": "request timeout",
          "ResultPath": "$.error.timeout"
        }
      ]
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
      "Default": "Request Expired"
    },
    "Request Expired": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue",
        "MessageBody": {
          "message.$": "States.Format('Jita request expired for {}.', $.requester_name )"
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
          "approver_name.$": "$.approver_name",
          "action": "append"
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
      "Next": "Approval Message",
      "OutputPath": "$.Payload"
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
          "message.$": "States.Format('Access for {} has expired. Permissions revoked successfully.', $.requester_arn )"
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
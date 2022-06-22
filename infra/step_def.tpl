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
      "Next": "Check if approved",
      "Catch": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "Next": "Error Messaging",
          "Comment": "request timeout",
          "ResultPath": "$.error.timeout"
        }
      ],
      "TimeoutSeconds": 3600
    },
    "Error Messaging": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.error.timeout",
          "IsPresent": true,
          "Next": "Send Reject Expired Message"
        },
        {
          "Variable": "$.error.malformed_policy",
          "IsPresent": true,
          "Next": "Send Malformed Policy Error"
        },
        {
          "Variable": "$.approved",
          "BooleanEquals": false,
          "Next": "Send Reject Rejected",
          "Comment": "Send Rejected Message"
        }
      ],
      "Default": "Send generic stack trace error"
    },
    "Send Reject Expired Message": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue",
        "MessageBody": {
          "message.$": "States.Format('Error for request {} has expired.', $.requester_name)"
        }
      },
      "End": true
    },
    "Check if approved": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.approved",
          "BooleanEquals": true,
          "Next": "Add user to role trust"
        },
        {
          "Variable": "$.approved",
          "BooleanEquals": false,
          "Next": "Error Messaging",
          "Comment": "Request rejected"
        }
      ]
    },
    "Send generic stack trace error": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue",
        "MessageBody": {
          "message.$": "States.Format('Error for request {}:  {}.', $.requester_name, $.error )"
        }
      },
      "End": true
    },
    "Add user to role trust": {
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
          "Next": "Error Messaging",
          "Comment": "Malformed Policy",
          "ResultPath": "$.error.malformed_policy"
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
      "Next": "Grant access time",
      "ResultPath": null
    },
    "Grant access time": {
      "Type": "Wait",
      "Seconds": 360,
      "Next": "Revoke user role access"
    },
    "Revoke user role access": {
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
    "Send Malformed Policy Error": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "MessageBody": {
          "message.$": "States.Format('Error for request {} has malformed resource policy. Verifiy requested ARN.', $.requester_name)"
        },
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue"
      },
      "End": true
    },
    "Send Reject Rejected": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jita-message-queue",
        "MessageBody": {
          "message.$": "States.Format('Request for {}  has been rejected by {}.', $.requester_name, $.approver_name )"
        }
      },
      "End": true
    }
  }
}

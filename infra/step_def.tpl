{
  "Comment": "A description of my state machine",
  "StartAt": "Send admin request",
  "States": {
    "Send admin request": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
      "Parameters": {
        "QueueUrl": "https://sqs.us-west-2.amazonaws.com/722461077209/jit-requests",
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
      "Next": "Choice"
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
      "Default": "Fail"
    },
    "Add to Trust": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${lambda_function_arn}",
        "Payload": {
          "requester_arn.$": "$.requester_arn",
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
      "Next": "Wait",
      "OutputPath": "$.Payload"
    },
    "Wait": {
      "Type": "Wait",
      "Seconds": 60,
      "Next": "Remove Trust"
    },
    "Remove Trust": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-west-2:722461077209:function:jit-modify-iam:$LATEST",
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
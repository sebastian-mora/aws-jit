# AWS-JIT

AWS Just in Time Admin. 

Request temporary Admin access 

## How it works

In the backend a step function controls the request and approval state. The core module can be expanded to support any integration. For right now only Slack is implemented.

1. A request is submitted to the Step function using the `StepFunctionClient.start_execution(message: Message)`

    The message object requires the following body but can be expanded.

    ```python
        message = Message({
            "requester_arn": requester_arn,
            "reason":  reason,
            "requester_name": requester_name
        })
    ```


2. A message with the input body is sent to SQS.
3. An integration polls the SQS and consumes the messages. 
4. Once the integration logic is completed to either approve or deny. A call can be made to `StepFunctionClient.send_success( message: Message, task_token: str)` or `StepFunctionClient.send_failure( message: Message, task_token: str)` 

    Note: the message body expects 

    ```python
        message = Message({
            "approver_name": approver_name,
            "requester_arn": sqs_body['input']['requester_arn']
        })
    ```
5. The state function now check if it was approved or not and continues down the correct path. If request is denied the state function end.

6. If approved the state function appends the `requester_arn` to a admin role.
8. A message is posted to jita-slack-messages queue to be forward to users. 
7. The function waits for the specified time (1hr default).
8. Finally the state function removed the `requester_arn` from the admin role trust policy and completes. 

## Custom Integration

Custom integration can be added. They must implement he flow from `core.StepFunctionClient` but any approval steps can be handled at the integration level including rbac controls on approvals. The `StepFunctionClient` simply provides an interface for the integration to send and receive data from the Step function. 

### Integration flow

1. Take user input and submit a message to `StepFunctionClient.start_execution(message: Message)`
2. Integration consumes request from SQS using `StepFunctionClient.getMessage()`
3. Integration decided approve or deny (user input, allow list, whatever)
4. Send update to state function `StepFunctionClient.send_success` `StepFunctionClient.send_failure`
5. Poll SQS Alert que to get updates for post in slack channel. Such as request approved or request denied. 

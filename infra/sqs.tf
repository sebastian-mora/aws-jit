resource "aws_sqs_queue" "jita_request_queue" {
  name                      = "jita-request-queue"
}

resource "aws_sqs_queue" "jita_message_queue" {
  name                      = "jita-message-queue"
}
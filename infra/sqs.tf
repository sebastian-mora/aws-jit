resource "aws_sqs_queue" "jita_request_queue" {
  name                      = "jita-request-queue"
  message_retention_seconds = var.jita_request_timout
}

resource "aws_sqs_queue" "jita_message_queue" {
  name                      = "jita-message-queue"
}
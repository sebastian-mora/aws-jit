resource "aws_sqs_queue" "jita_queue" {
  name                      = "jita-request-queue"
}

resource "aws_sqs_queue" "jita_queue" {
  name                      = "jita-message-queue"
}
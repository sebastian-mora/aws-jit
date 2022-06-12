resource "aws_sqs_queue" "jita_queue" {
  name                      = "jita-request-queue"
}
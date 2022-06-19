output "sqs_url" {
  value = aws_sqs_queue.jita_request_queue.url
}

output "step_function_arn" {
  value = module.step_function.state_machine_arn
}
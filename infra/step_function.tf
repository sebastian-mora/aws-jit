

data "template_file" "step_def"{
    template = file("${path.module}/step_def.tpl")
    vars = {
      "lambda_function_arn" = module.jita_modifiy_iam.lambda_function_arn
    }
}

module "step_function" {
    source = "terraform-aws-modules/step-functions/aws"
    type = "STANDARD"
    cloudwatch_log_group_name = "/aws/vendedlogs/states/jita-Logs"
    name       = "jita-requests"
    definition = data.template_file.step_def.rendered

    service_integrations = {sqs={sqs=[aws_sqs_queue.jita_queue.arn]}}
}
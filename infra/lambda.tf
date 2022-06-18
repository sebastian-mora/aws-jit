module "jita_modifiy_iam" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "jita_modifiy_iam"
  description   = "Modified jita role to allow user access"
  handler       = "index.lambda_handler"
  runtime       = "python3.9"
  attach_policy = true
  policy = aws_iam_policy.lambda_modifiy_jita_admin_role.arn
  source_path = "src/index.py"

  environment_variables = {
    ADMIN_ROLE_NAME = aws_iam_role.jita_admin.name
  }

}
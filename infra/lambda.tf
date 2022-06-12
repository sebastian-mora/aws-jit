module "jita_modifiy_iam" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "jita_modifiy_iam"
  description   = "Modified jita role to allow user access"
  handler       = "index.lambda_handler"
  runtime       = "python3.9"
  lambda_role = aws_iam_role.lambda_jita_modifiy_iam_role.arn
  source_path = "src/index.py"

  environment_variables = {
    ADMIN_ROLE_NAME = aws_iam_role.jita_admin.name
  }

}
module "jita_modifiy_iam" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "jita_modifiy_iam"
  description   = "Modified jita role to allow user access"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"

  source_path = "src/index.py"

}
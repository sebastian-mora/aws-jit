data "aws_iam_policy_document" "lambda_modifiy_jita_admin_role" {
  statement {
    sid = "1"

    actions = [
      "iam:GetRole",
      "iam:UpdateAssumeRolePolicy",
    ]

    resources = [
      "arn:aws:s3:::*"
    ]
  }

}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = [ "lambda.amazonaws.com" ]
    }
  }
}

resource "aws_iam_policy" "lambda_modifiy_jita_admin_role" {
  name = "lambda_modifiy_jita_admin_role"
  description = "Allows modificaiton of jita-admin trust policy."
  policy = data.aws_iam_policy_document.lambda_modifiy_jita_admin_role.json
}

resource "aws_iam_role" "lambda_jita_modifiy_iam_role" {
  name               = "lambda_jita_modifiy_iam"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "attached_lambda_policy" {
  role = aws_iam_role.lambda_jita_modifiy_iam_role.name
  policy_arn = aws_iam_policy.lambda_modifiy_jita_admin_role.arn
}

resource "aws_iam_role" "jita_admin" {
  name = "jita-admin"
  assume_role_policy = data.aws_iam_policy_document.jita_admin_assume_role.json
}

data "aws_iam_policy_document" "jita_admin_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = [ "arn:aws:iam::722461077209:role/aws-jit-dev-us-west-2-lambdaRole" ]
    }
    condition {
      test = "StringLike"
      variable = "sts:RoleSessionName"

      values = ["$${aws:username}"]
    }
  }
}

# resource "aws_iam_role_policy_attachment" "jita_admin_attach" {
#   name = aws_iam_role.jita_admin.name
#   policy_arn = 
# }
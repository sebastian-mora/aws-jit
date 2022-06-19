data "aws_iam_policy_document" "lambda_modifiy_jita_admin_role" {
  statement {
    sid = "1"

    actions = [
      "iam:GetRole",
      "iam:UpdateAssumeRolePolicy",
    ]

    resources = [
      aws_iam_role.jita_admin.arn,
    ]
  }

}


resource "aws_iam_policy" "lambda_modifiy_jita_admin_role" {
  name = "lambda_modifiy_jita_admin_role"
  description = "Allows modificaiton of jita-admin trust policy."
  policy = data.aws_iam_policy_document.lambda_modifiy_jita_admin_role.json
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


data "aws_iam_policy_document" "step_function_trust_policy" {
    statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = [ "states.amazonaws.com" ]
    }
  }
}

data "aws_iam_policy_document" "step_function_permissions" {
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]

    resources = [
      format("%s:*", module.jita_modifiy_iam.lambda_function_arn)
    ]
  }

  statement {
    actions = ["sqs:SendMessage"]
    resources = [ aws_sqs_queue.jita_request_queue.arn, aws_sqs_queue.jita_message_queue.arn  ]
  }
}

resource "aws_iam_policy" "step_function_execution" {
  name = "step_function_execution"
  description = "Allows step fucntion to run."
  policy = data.aws_iam_policy_document.step_function_permissions.json
}

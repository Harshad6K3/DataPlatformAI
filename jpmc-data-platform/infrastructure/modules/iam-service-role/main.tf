variable "name" {
  type = string
}

variable "trusted_services" {
  type    = list(string)
  default = ["ecs-tasks.amazonaws.com"]
}

variable "secret_arns" {
  type = list(string)
}

data "aws_iam_policy_document" "trust" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = var.trusted_services
    }
  }
}

resource "aws_iam_role" "this" {
  name               = var.name
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

data "aws_iam_policy_document" "secrets_read" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetSecretValue"
    ]
    resources = var.secret_arns
  }
}

resource "aws_iam_role_policy" "secrets_read" {
  name   = "read-application-secrets"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.secrets_read.json
}

output "arn" {
  value = aws_iam_role.this.arn
}

output "name" {
  value = aws_iam_role.this.name
}

variable "name_prefix" {
  type = string
}

variable "secrets" {
  type      = map(string)
  sensitive = true
}

variable "secret_names" {
  type = list(string)
}

variable "recovery_window_in_days" {
  type    = number
  default = 7
}

resource "aws_secretsmanager_secret" "this" {
  for_each = toset(var.secret_names)

  name                    = "${var.name_prefix}/${each.key}"
  recovery_window_in_days = var.recovery_window_in_days
}

resource "aws_secretsmanager_secret_version" "this" {
  for_each = toset(var.secret_names)

  secret_id     = aws_secretsmanager_secret.this[each.key].id
  secret_string = var.secrets[each.key]
}

output "arns" {
  value = { for key, secret in aws_secretsmanager_secret.this : key => secret.arn }
}

output "names" {
  value = { for key, secret in aws_secretsmanager_secret.this : key => secret.name }
}

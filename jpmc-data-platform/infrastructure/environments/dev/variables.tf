variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "secret_values" {
  description = "Secret values as JSON strings. Supplied through a protected tfvars file or CI variables."
  type        = map(string)
  sensitive   = true
}

variable "secret_names" {
  type    = list(string)
  default = ["ANTHROPIC_API_KEY", "DATABASE_URL", "REDIS_URL"]
}

variable "trusted_services" {
  description = "AWS services allowed to assume the application role."
  type        = list(string)
  default     = ["ecs-tasks.amazonaws.com"]
}

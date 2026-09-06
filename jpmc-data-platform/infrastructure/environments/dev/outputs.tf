output "secret_names" {
  description = "Names to use as SecretId values with Secrets Manager."
  value       = module.secrets.names
}

output "application_role_arn" {
  description = "Attach this role to the deployed application workload."
  value       = module.application_role.arn
}

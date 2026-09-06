module "secrets" {
  source = "../../modules/secrets-manager"

  name_prefix = "jpmc-data-platform/${var.environment}"
  secret_names = var.secret_names
  secrets     = var.secret_values
}

module "application_role" {
  source = "../../modules/iam-service-role"

  name            = "jpmc-data-platform-${var.environment}-application"
  trusted_services = var.trusted_services
  secret_arns     = values(module.secrets.arns)
}

module "networking" {
  source = "../../modules/networking"

  vpc_cidr           = "10.42.0.0/16"
  environment        = var.environment
  az_count           = 2
  enable_nat_gateway = false
}

module "aurora" {
  source = "../../modules/aurora-postgres"

  cluster_identifier = "jpmc-data-platform-${var.environment}"
  database_name      = "dataplatform"
  min_capacity       = 0.5
  max_capacity       = 4
  vpc_id             = module.networking.vpc_id
  subnet_ids         = module.networking.private_subnet_ids
}

module "pipeline_queue" {
  source = "../../modules/sqs-queue"

  queue_name = "jpmc-data-platform-${var.environment}-pipeline"
  is_fifo    = false
  environment = var.environment
}

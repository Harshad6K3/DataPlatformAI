resource "aws_kms_key" "this" {
  description         = "KMS key for ${var.cluster_identifier} Aurora storage"
  enable_key_rotation = true
}

resource "aws_secretsmanager_secret" "this" {
  name                    = "${var.cluster_identifier}/credentials"
  description             = "Aurora credentials for ${var.cluster_identifier}"
  kms_key_id              = aws_kms_key.this.arn
  recovery_window_in_days = 7
}

resource "random_password" "master" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  secret_string = jsonencode({
    username = "platform_admin"
    password = random_password.master.result
  })
}

resource "aws_db_subnet_group" "this" {
  name       = var.cluster_identifier
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "this" {
  name        = "${var.cluster_identifier}-aurora"
  description = "Aurora access for ${var.cluster_identifier}"
  vpc_id      = var.vpc_id
}

resource "aws_rds_cluster" "this" {
  cluster_identifier              = var.cluster_identifier
  engine                          = "aurora-postgresql"
  engine_mode                     = "provisioned"
  database_name                   = var.database_name
  master_username                 = "platform_admin"
  master_password                 = random_password.master.result
  db_subnet_group_name            = aws_db_subnet_group.this.name
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.this.arn
  backup_retention_period         = 7
  skip_final_snapshot             = true
  db_cluster_parameter_group_name = null

  serverlessv2_scaling_configuration {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }
}

resource "aws_rds_cluster_instance" "this" {
  identifier         = "${var.cluster_identifier}-instance-1"
  cluster_identifier = aws_rds_cluster.this.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.this.engine
  engine_version     = aws_rds_cluster.this.engine_version
}
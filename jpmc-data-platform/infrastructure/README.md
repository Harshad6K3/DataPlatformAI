# AWS infrastructure

The `environments/dev` configuration provisions the AWS secret store and an application IAM role.

## Deploy

From `infrastructure/environments/dev`:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with real values; keep it uncommitted.
terraform init
terraform plan
terraform apply
```

Or use the deployment wrapper, which verifies the AWS identity and applies the reviewed plan:

```powershell
.\deploy.ps1 -Profile jpmc-dev
```

Use `-AutoApprove` only in a controlled CI/CD job:

```powershell
.\deploy.ps1 -Profile jpmc-dev -AutoApprove
```

Terraform uses the standard AWS credential chain. Authenticate with an AWS profile or OIDC-based CI role, for example:

```powershell
aws sso login --profile jpmc-dev
$env:AWS_PROFILE = "jpmc-dev"
```

The resulting IAM role grants only `DescribeSecret` and `GetSecretValue` for the secrets created by this stack. Attach `application_role_arn` to the ECS task role or adapt `trusted_services` for another AWS runtime.

Secret values are stored in Terraform state, so use an encrypted remote backend with restricted access before production deployment. Do not commit `terraform.tfvars` or place long-lived AWS keys in the repository.

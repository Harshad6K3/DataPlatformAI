[CmdletBinding()]
param(
    [string]$Profile = $env:AWS_PROFILE,
    [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    throw "Terraform is not installed or is not on PATH."
}

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    throw "AWS CLI is not installed or is not on PATH."
}

if (-not (Test-Path "terraform.tfvars")) {
    throw "terraform.tfvars is missing. Copy terraform.tfvars.example and add the deployment values."
}

if ($Profile) {
    $env:AWS_PROFILE = $Profile
}

Write-Host "Checking AWS identity..."
aws sts get-caller-identity

Write-Host "Initializing Terraform..."
terraform init

Write-Host "Creating deployment plan..."
terraform plan -out=tfplan

if ($AutoApprove) {
    Write-Host "Applying deployment plan..."
    terraform apply tfplan
} else {
    $confirmation = Read-Host "Apply this plan to AWS? Type APPLY to continue"
    if ($confirmation -eq "APPLY") {
        terraform apply tfplan
    } else {
        Write-Host "Plan was created but not applied."
    }
}

Write-Host "Deployment script completed."

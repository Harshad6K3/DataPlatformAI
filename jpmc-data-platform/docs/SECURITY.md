# Security Overview

## Data classification

| Level | Description | Handling |
| --- | --- | --- |
| Public | Information approved for public release | May be displayed without access control |
| Internal | Non-public business information | Authenticated workforce access; do not publish |
| Confidential | Sensitive business, operational, or client information | Least-privilege access, encryption, and audit logging |
| PII | Information that identifies or can identify a person | Treat as Confidential or higher; minimize, mask, and restrict access |

## Authentication flow

Requests enter through the service API and are checked by shared authentication middleware. The middleware validates bearer token signatures and claims against the configured JWKS issuer, then attaches the authenticated user context to the request. Protected routes reject missing or invalid credentials before business logic executes. The frontend supports a local mock mode only for development.

## Audit logging coverage

The shared audit layer records authenticated user identity, request metadata, service/action, outcome, and correlation identifiers for API activity and material data changes. Logs are redacted before being sent to configured sinks such as stdout, CloudWatch, or S3. Audit events must not contain raw credentials, tokens, or unmasked PII.

## Secret management

Secrets are stored in AWS Secrets Manager and referenced by deployment configuration or runtime secret lookup. Terraform creates encrypted secret resources and uses KMS-backed storage. Values belong in protected environment or CI variables and must never be committed to source control. Access is granted through least-privilege IAM roles.

## Claude API sanitisation rules

- Remove API keys, bearer tokens, passwords, connection strings, and other credential material.
- Mask direct identifiers and PII unless the approved task requires them.
- Reject or neutralize prompt-injection patterns that attempt to override system controls or exfiltrate context.
- Send only the minimum data needed for the task and prefer structured, bounded outputs.
- Audit the sanitisation decision and preserve only redacted prompt metadata.
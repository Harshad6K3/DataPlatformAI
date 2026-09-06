# JPMC AI Data Platform

The JPMC AI Data Platform gives the Chief Data Office a governed operating layer for discovering, understanding, and reconciling enterprise data. It combines catalog, governance, lineage, pipeline, and reconciliation services with a shared security, audit, AWS, database, and Claude foundation so teams can ship trustworthy data capabilities with consistent controls and measurable AI cost.

## Architecture

```mermaid
flowchart LR
	UI[React platform shell] --> API[Service APIs]
	API --> C[Catalog :8001]
	API --> G[Governance :8002]
	API --> L[Lineage :8003]
	API --> P[Pipeline agent :8004]
	API --> R[Recon agent :8005]
	C & G & L & P & R --> Shared[Shared foundation<br/>Auth | Audit | AWS clients | DB | Claude client]
	Shared --> Aurora[(Aurora PostgreSQL)]
	Shared --> SQS[SQS + DLQ]
	Shared --> S3[(S3)]
	Shared --> SM[Secrets Manager + KMS]
	P & R --> Claude[Claude Haiku / Sonnet]
```

## Quick start

```powershell
git clone <repository-url>
Set-Location jpmc-data-platform
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Set-Location frontend
npm install
$env:VITE_AUTH_MODE = "mock"
npm run dev -- --host 0.0.0.0
```

Open [http://localhost:5173](http://localhost:5173). Infrastructure validation runs from `infrastructure/environments/dev` with `terraform init` followed by `terraform validate`.

## Services

| Service | Port | Status |
| --- | ---: | --- |
| Catalog | 8001 | Foundation |
| Governance | 8002 | Foundation |
| Lineage | 8003 | Foundation |
| Pipeline agent | 8004 | Foundation |
| Recon agent | 8005 | Foundation |

## Documentation

- [Architecture decisions](docs/ARCHITECTURE_DECISIONS.md)
- [Security overview](docs/SECURITY.md)
- [Infrastructure guide](infrastructure/README.md)
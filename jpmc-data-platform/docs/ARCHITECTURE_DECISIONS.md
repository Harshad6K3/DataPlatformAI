# Architecture Decision Records

## ADR-001: FastAPI over Django

**Status:** Accepted

FastAPI is the service framework because the platform is API-first, async, and composed of focused services. Native async support, Pydantic validation, OpenAPI generation, and low operational overhead fit the data and AI workloads better than Django's broader monolith-oriented framework.

## ADR-002: Aurora Serverless v2 over fixed RDS

**Status:** Accepted

Aurora Serverless v2 provides PostgreSQL compatibility with capacity that can scale with workload demand. It reduces idle cost for development and variable AI workloads while retaining managed backups, encryption, and multi-AZ durability.

## ADR-003: Claude tool use over LangChain

**Status:** Accepted

The platform uses Claude's native tool-use contract through the shared client. Direct integration keeps prompts, schemas, retries, cost tracking, and audit behavior visible to the team, avoiding an additional orchestration abstraction and its transitive dependencies.

## ADR-004: Two-tier LLM strategy (Haiku + Sonnet)

**Status:** Accepted

Claude Haiku handles high-volume classification, extraction, and routine routing. Claude Sonnet handles ambiguous reasoning, complex reconciliation, and higher-value analysis. Services select the tier by task policy, with cost and latency recorded in the shared client.

## ADR-005: Prompt sanitisation before Claude API

**Status:** Accepted

All prompts pass through the shared sanitiser before leaving the platform. It removes or masks secrets and sensitive identifiers, limits unsafe instruction patterns, and records a redacted sanitisation event for audit.
# Secure Agent Deployment Proof

Public workbench for a production-style agent deployment artifact.

The goal is to show how an enterprise AI workflow moves from discovery to a running prototype, then through evals, permission boundaries, telemetry, rollout planning, and inference cost assumptions.

## Scope

- Issue or incident intake with repository and document context
- Agent workflow with explicit tool boundaries and human review
- MCP-style inventory for tools, data access, and permissions
- Eval suite with pass/fail gates and red-team cases
- Trace, metric, and audit evidence for the workflow
- Rollout memo for an engineering or platform leader
- Inference economics notes for latency, throughput, and cost assumptions

## Planned Artifacts

| Artifact | Purpose | Status |
| --- | --- | --- |
| `architecture/` | System diagram, trust boundaries, and deployment notes | Planned |
| `workflow/` | Minimal runnable agent workflow | Planned |
| `evals/` | Regression, safety, and red-team checks | Planned |
| `telemetry/` | Trace and metric examples | Planned |
| `inference/` | TTFT, TPOT, throughput, p95/p99, and cost assumptions | Planned |
| `rollout/` | Customer-facing production rollout memo | Planned |

## Design Principles

- Keep the demo small enough to inspect.
- Treat tool access as a security boundary.
- Prefer measured behavior over broad claims.
- Show tradeoffs and failure modes.
- Make every artifact reusable as a technical interview or architecture-review asset.

## Current Status

The first implementation is an offline Python scaffold: a deterministic status CLI, tests, packaging, CI, and a nonroot container definition. The artifact directories above remain planned. Agent execution, cloud deployment, OAuth, live evals, and telemetry are not implemented; deployment readiness is not assessed.

The CLI reads no credentials, makes no network requests, and reports declared scaffold capabilities. Exit code 0 means the report rendered successfully; it does not certify deployment readiness. Invalid arguments exit 2 without echoing supplied values.

## Local Setup and Usage

Requires Python 3.12 or newer. Runtime dependencies are empty. Installing the package and development tools requires package-index access; running the installed CLI is offline.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
secure-agent-proof status
secure-agent-proof status --format json
python -m secure_agent_deployment_proof status --format json
```

The JSON schema has version 1, `status: "scaffold"`, `execution_mode: "offline"`, and `deployment_readiness: "not_assessed"`, plus explicit implemented and unimplemented capability lists. Output is stable across repeated runs and independent of cloud access.

## Validation

```sh
ruff check src tests
ruff format --check src tests
mypy
coverage run -m unittest discover -s tests -v
coverage report
python -m build
pip-audit
```

Tests cover truthful status, independent report objects, text/JSON output, invalid arguments, and help. A packaging integration test builds a wheel, installs it without dependencies in a temporary virtual environment, then exercises its installed console and module entry points outside the checkout. Coverage includes branches and enforces an 80% minimum.

CI runs these checks on Python 3.12, builds the distributions, audits development dependencies, and builds/runs the container. An actual CI pass must be verified from the workflow run; the presence of its definition is not execution evidence.

## Container Smoke

Requires a running Docker daemon. Building requires registry/package-index access; the smoke run has networking disabled, a read-only filesystem, and all Linux capabilities dropped.

```sh
docker build -t secure-agent-proof .
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges secure-agent-proof
```

The image runs as numeric user/group `10001:10001` and exposes no service port. This proves only that the offline report can run in a container; no production deployment or security certification is claimed.

"""Describe implemented capabilities without claiming deployment readiness."""

from typing import TypedDict


class StatusReport(TypedDict):
    schema_version: int
    status: str
    execution_mode: str
    deployment_readiness: str
    implemented: list[str]
    not_implemented: list[str]


def status_report() -> StatusReport:
    """Return a fresh deterministic report, independent of environment or network."""
    return {
        "schema_version": 1,
        "status": "scaffold",
        "execution_mode": "offline",
        "deployment_readiness": "not_assessed",
        "implemented": ["deterministic_status_cli"],
        "not_implemented": [
            "agent_workflow",
            "cloud_deployment",
            "oauth",
            "live_evals",
            "telemetry",
        ],
    }

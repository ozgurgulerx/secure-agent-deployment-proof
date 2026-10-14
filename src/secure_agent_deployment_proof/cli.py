"""Render scaffold status locally without credentials or external services."""

import argparse
import json
import sys
from collections.abc import Sequence
from typing import NoReturn

from .readiness import status_report


class SafeArgumentParser(argparse.ArgumentParser):
    """Keep invalid arguments (which might contain secrets) out of error output."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, "error: invalid arguments; use --help for supported options\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Report capabilities; exit zero means report rendered, never deployment ready."""
    parser = SafeArgumentParser(description="Inspect the offline workbench scaffold status.")
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="Show implemented capabilities and limitations")
    status.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    report = status_report()
    if args.format == "json":
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        print(f"Status: {report['status']}")
        print(f"Execution mode: {report['execution_mode']}")
        print(f"Deployment readiness: {report['deployment_readiness']}")
        print(f"Implemented: {', '.join(report['implemented'])}")
        print(f"Not implemented: {', '.join(report['not_implemented'])}")
    return 0

"""Main entry point for Document Validation Engine desktop application."""

from __future__ import annotations

from pathlib import Path

from bootstrap.bootstrap import bootstrap_container
from gui.app import run_gui


def main() -> int:
	"""Initialize application services and launch GUI."""
	root_path = Path(__file__).resolve().parent
	# Bootstraps configuration, logging, DI and event bus wiring.
	container = bootstrap_container(root_path)
	return run_gui(root_path, container)


if __name__ == "__main__":
	raise SystemExit(main())


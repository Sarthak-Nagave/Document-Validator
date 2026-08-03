"""Build structured report payloads from validation results."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from collections import Counter
from typing import Any

from domain.value_objects.validation_result import ValidationResult


class ReportBuilder:
	"""Transforms rich result objects into JSON-serializable dictionaries."""

	def build(self, results: list[ValidationResult]) -> dict[str, Any]:
		"""Build report payload for all configured exporters."""
		items = [self._serialize_result(result) for result in results]
		status_counter = Counter((item.get("status") or "UNKNOWN") for item in items)
		folder_counter = Counter((item.get("root_group") or "UNKNOWN") for item in items)

		return {
			"generated_at": datetime.utcnow().isoformat(),
			"total": len(results),
			"summary": {
				"status_counts": dict(status_counter),
				"folder_counts": dict(folder_counter),
				"pass_count": status_counter.get("SUCCESS", 0),
				"warning_count": status_counter.get("WARNING", 0),
				"fail_count": status_counter.get("FAILED", 0) + status_counter.get("ERROR", 0),
			},
			"items": items,
			"results": items,
		}

	def _serialize_result(self, result: ValidationResult) -> dict[str, Any]:
		data = asdict(result) if is_dataclass(result) else dict(result)
		task = data.get("task")
		if task and isinstance(task, dict) and "file_path" in task:
			task["file_path"] = str(task["file_path"])
		return data


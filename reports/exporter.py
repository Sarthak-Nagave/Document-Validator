"""Report exporters writing JSON, HTML and XLSX artifacts."""

from __future__ import annotations

from pathlib import Path
import json

import openpyxl


class ReportExporter:
	"""Concrete exporter set producing all required report artifacts."""

	def export_json(self, payload: dict, target_dir: Path) -> Path:
		"""Write JSON report payload to disk."""
		out_path = target_dir / "Validation_Report.json"
		out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
		return out_path

	def export_html(self, payload: dict, target_dir: Path) -> Path:
		"""Render a lightweight enterprise-styled HTML report."""
		out_path = target_dir / "Validation_Report.html"
		rows = []
		summary = payload.get("summary", {})
		for item in payload.get("items", []):
			task = item.get("task") or {}
			excel = item.get("excel_result") or {}
			crypto = excel.get("crypto_result") or {}
			warnings = ", ".join(item.get("warning_list", []) or [])
			errors = ", ".join(item.get("error_list", []) or [])
			rows.append(
				"<tr>"
				f"<td>{task.get('file_name', '')}</td>"
				f"<td>{task.get('root_group', '')}</td>"
				f"<td>{task.get('extension', '')}</td>"
				f"<td>{item.get('validator_name', '')}</td>"
				f"<td>{item.get('status', '')}</td>"
				f"<td>{item.get('reason', '')}</td>"
				f"<td>{excel.get('sheet1_signer', '')}</td>"
				f"<td>{excel.get('approved_by_signer', '')}</td>"
				f"<td>{excel.get('signer_match', '')}</td>"
				f"<td>{excel.get('public_key', '')}</td>"
				f"<td>{excel.get('payload_sha256', '')}</td>"
				f"<td>{excel.get('expected_payload_sha256', '')}</td>"
				f"<td>{excel.get('payload_status', '')}</td>"
				f"<td>{crypto.get('verification_status', '')}</td>"
				f"<td>{crypto.get('verification_profile', '')}</td>"
				f"<td>{warnings}</td>"
				f"<td>{errors}</td>"
				"</tr>"
			)
		html = (
			"<html><head><meta charset='utf-8'><title>DVE Report</title>"
			"<style>body{font-family:Segoe UI;background:#f7f7f7;color:#333}"
			"table{width:100%;border-collapse:collapse;background:white}"
			"th,td{border:1px solid #ddd;padding:8px}th{background:#ff7a00;color:white}</style>"
			"</head><body><h1>Document Validation Report</h1>"
			f"<p>Total Results: {payload.get('total', 0)}</p>"
			f"<p>PASS: {summary.get('pass_count', 0)} | WARNING: {summary.get('warning_count', 0)} | FAIL: {summary.get('fail_count', 0)}</p>"
			"<table><thead><tr><th>File</th><th>Folder</th><th>Type</th><th>Validator</th><th>Status</th><th>Reason</th><th>Sheet1 Signer</th><th>Approved By</th><th>Signer Match</th><th>Public Key</th><th>Payload SHA256</th><th>Expected SHA256</th><th>Payload Status</th><th>Crypto Status</th><th>Profile</th><th>Warnings</th><th>Errors</th></tr></thead>"
			f"<tbody>{''.join(rows)}</tbody></table></body></html>"
		)
		out_path.write_text(html, encoding="utf-8")
		return out_path

	def export_xlsx(self, payload: dict, target_dir: Path) -> Path:
		"""Write summary workbook report."""
		out_path = target_dir / "Validation_Report.xlsx"
		wb = openpyxl.Workbook()
		ws = wb.active
		ws.title = "Summary"
		ws.append([
			"Workbook",
			"Folder",
			"Type",
			"Validator",
			"Overall Result",
			"Reason",
			"Sheet1 Signer",
			"Approved By",
			"Signer Match",
			"Public Key",
			"Payload SHA256",
			"Expected Payload SHA256",
			"Payload Status",
			"Signature Status",
			"Crypto Status",
			"Verification Profile",
			"Warnings",
			"Errors",
		])
		for item in payload.get("items", []):
			task = item.get("task") or {}
			excel = item.get("excel_result") or {}
			crypto = excel.get("crypto_result") or {}
			ws.append(
				[
					task.get("file_name", ""),
					task.get("root_group", ""),
					task.get("extension", ""),
					item.get("validator_name", ""),
					item.get("status", ""),
					item.get("reason", ""),
					excel.get("sheet1_signer", ""),
					excel.get("approved_by_signer", ""),
					excel.get("signer_match", ""),
					excel.get("public_key", ""),
					excel.get("payload_sha256", ""),
					excel.get("expected_payload_sha256", ""),
					excel.get("payload_status", ""),
					crypto.get("reason", ""),
					crypto.get("verification_status", ""),
					crypto.get("verification_profile", ""),
					"; ".join(item.get("warning_list", []) or []),
					"; ".join(item.get("error_list", []) or []),
				]
			)
		wb.save(out_path)
		return out_path


from pathlib import Path
from bootstrap.bootstrap import bootstrap_container
import json
import collections

root = Path('.').resolve()
container = bootstrap_container(root)
results = container.engine.run('C:/Users/SM 464/Desktop/DOC/DS0')
excel = [r for r in results if str(r.task.extension).lower() == '.xlsx']

summary = {
    "excel_count": len(excel),
    "excel_status": dict(collections.Counter(str(r.status.value if hasattr(r.status, 'value') else r.status) for r in excel)),
    "samples": [],
}

seen_signers = set()
for r in excel:
    er = r.excel_result
    if not er:
        continue
    signer = (er.sheet1_signer or '').strip().lower()
    if signer in seen_signers:
        continue
    seen_signers.add(signer)
    cr = er.crypto_result
    summary["samples"].append({
        "file": r.task.file_name,
        "sheet1_signer": er.sheet1_signer,
        "approved_by": er.approved_by_signer,
        "signer_match": er.signer_match,
        "payload_status": er.payload_status,
        "payload_strategy": er.payload_strategy,
        "payload_sha256": er.payload_sha256,
        "expected_sha256": er.expected_payload_sha256,
        "crypto_status": cr.verification_status.value if hasattr(cr.verification_status, 'value') else str(cr.verification_status),
        "crypto_reason": cr.reason,
        "sig_len": cr.signature_length,
        "payload_len": cr.payload_length,
    })

print("EXCEL_SUMMARY_JSON_START")
print(json.dumps(summary, indent=2))
print("EXCEL_SUMMARY_JSON_END")

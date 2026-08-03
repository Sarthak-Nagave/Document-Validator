import logging
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from domain.enums.validation_status import ValidationStatus
from events.event_types import EventType

class ValidationWorker(QThread):
    # PySide signals consumed by GUI widgets.
    progress_updated = Signal(dict)
    log_emitted = Signal(dict)
    dashboard_updated = Signal(dict)
    result_added = Signal(object)
    validation_completed = Signal(dict)
    validation_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, engine, container, target_folder, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.container = container
        self.target_folder = target_folder
        self.is_cancelled = False
        self._results = []
        self._discovered_files = 0
        self._processed_files = 0
        self._current_file = "-"
        self._start_time = 0.0
        self._root_name = Path(target_folder).name if target_folder else ""
        self._setup_event_bus()

    def _setup_event_bus(self):
        bus = self.container.event_bus
        self._bus = bus
        bus.subscribe(EventType.FILE_DISCOVERED, self._on_file_found)
        bus.subscribe(EventType.SCAN_STARTED, self._on_scan_started)
        bus.subscribe(EventType.VALIDATION_STARTED, self._on_val_started)
        bus.subscribe(EventType.VALIDATION_FAILED, self._on_val_failed)
        bus.subscribe(EventType.VALIDATION_COMPLETED, self._on_val_completed)
        bus.subscribe(EventType.VALIDATION_SKIPPED, self._on_val_skipped)
        bus.subscribe(EventType.APPLICATION_SHUTDOWN, self._on_shutdown)
        
        # We could also intercept standard logs by adding a custom logging handler
        self._setup_log_interceptor()

    def _setup_log_interceptor(self):
        class SignalHandler(logging.Handler):
            def __init__(self, sig):
                super().__init__()
                self.sig = sig
            def emit(self, record):
                # We can format the message and emit
                msg = {
                    "timestamp": self.formatter.formatTime(record, "%H:%M:%S") if self.formatter else "",
                    "severity": record.levelname,
                    "module": record.module,
                    "message": record.getMessage()
                }
                self.sig.emit(msg)
                
        handler = SignalHandler(self.log_emitted)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s]: %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        self._handler = handler

    def run(self):
        self._start_time = time.time()
        self._emit_progress(stage="Validation Started", current_file="-", status="Validation Started")
        try:
            self._results = self.engine.run(self.target_folder)

            # Report generation occurs in engine.run before it returns.
            self._emit_progress(stage="Generating Reports", current_file="-", status="Generating Reports")

            elapsed = max(time.time() - self._start_time, 0.0)
            self._processed_files = len(self._results)
            self._discovered_files = max(self._discovered_files, self._processed_files)
            final_stats = self._compute_stats(self._results, elapsed, progress=100.0)
            report_paths = self._discover_reports()

            self.dashboard_updated.emit(final_stats)
            self._emit_progress(stage="Completed", current_file="-", status="Validation Completed Successfully", force_progress=100.0)
            self.validation_completed.emit(
                {
                    "results": self._results,
                    "stats": final_stats,
                    "report_paths": report_paths,
                    "elapsed": elapsed,
                    "root_name": self._root_name,
                }
            )
        except Exception as e:
            self._emit_progress(stage="Failed", current_file=self._current_file, status="Validation Failed")
            self.error_occurred.emit(str(e))
        finally:
            logging.getLogger().removeHandler(self._handler)
            self._bus.unsubscribe(EventType.FILE_DISCOVERED, self._on_file_found)
            self._bus.unsubscribe(EventType.SCAN_STARTED, self._on_scan_started)
            self._bus.unsubscribe(EventType.VALIDATION_STARTED, self._on_val_started)
            self._bus.unsubscribe(EventType.VALIDATION_FAILED, self._on_val_failed)
            self._bus.unsubscribe(EventType.VALIDATION_COMPLETED, self._on_val_completed)
            self._bus.unsubscribe(EventType.VALIDATION_SKIPPED, self._on_val_skipped)
            self._bus.unsubscribe(EventType.APPLICATION_SHUTDOWN, self._on_shutdown)
            self.validation_finished.emit()

    def cancel(self):
        self.is_cancelled = True
        self._emit_progress(stage="Cancelling", current_file=self._current_file, status="Cancellation Requested")

    def _discover_reports(self) -> dict:
        report_dir = Path("output") / "reports"
        return {
            "html": str(report_dir / "Validation_Report.html"),
            "xlsx": str(report_dir / "Validation_Report.xlsx"),
            "json": str(report_dir / "Validation_Report.json"),
        }

    def _compute_stats(self, results, elapsed: float, progress: float | None = None) -> dict:
        total = len(results)
        pdf_count = 0
        excel_count = 0
        pass_count = 0
        fail_count = 0
        warning_count = 0
        skipped_count = 0

        for res in results:
            ext = (getattr(getattr(res, "task", None), "extension", "") or "").lower()
            if ext == ".pdf":
                pdf_count += 1
            elif ext == ".xlsx":
                excel_count += 1

            status = getattr(res, "status", ValidationStatus.FAILED)
            status_value = status.value if hasattr(status, "value") else str(status)
            status_upper = status_value.upper()

            if status_upper == ValidationStatus.SUCCESS.value:
                pass_count += 1
            elif status_upper == ValidationStatus.WARNING.value:
                warning_count += 1
            elif status_upper == ValidationStatus.SKIPPED.value:
                skipped_count += 1
            else:
                fail_count += 1

        elapsed_safe = max(elapsed, 1e-9)
        speed = total / elapsed_safe
        progress_value = progress if progress is not None else (100.0 * self._processed_files / self._discovered_files if self._discovered_files else 0.0)
        progress_value = max(0.0, min(100.0, progress_value))

        return {
            "Total": total,
            "PDF": pdf_count,
            "Excel": excel_count,
            "PASS": pass_count,
            "FAIL": fail_count,
            "WARNING": warning_count,
            "SKIPPED": skipped_count,
            "Execution Time": f"{elapsed:.2f}s",
            "Validation Speed": f"{speed:.2f}/s",
            "Progress": f"{progress_value:.0f}%",
        }

    def _emit_progress(self, stage: str, current_file: str, status: str, force_progress: float | None = None):
        elapsed = max(time.time() - self._start_time, 0.0)
        total = self._discovered_files
        processed = self._processed_files
        remaining = max(total - processed, 0)
        if force_progress is None:
            progress = 100.0 * processed / total if total > 0 else 0.0
        else:
            progress = force_progress
        progress = max(0.0, min(100.0, progress))

        speed = (processed / elapsed) if elapsed > 0 else 0.0
        eta = (remaining / speed) if speed > 0 else 0.0

        self.progress_updated.emit(
            {
                "stage": stage,
                "status": status,
                "current_file": current_file or "-",
                "processed": processed,
                "remaining": remaining,
                "total": total,
                "progress": progress,
                "speed": speed,
                "eta_seconds": eta,
                "elapsed_seconds": elapsed,
            }
        )
            
    # Callbacks to route EventBus -> PySide Signals
    def _on_scan_started(self, payload):
        self._emit_progress(stage="Scanning", current_file=str(payload), status="Scanning")

    def _on_file_found(self, payload):
        if self.is_cancelled:
            self._emit_progress(stage="Cancelled", current_file="-", status="Cancelled")
            return
        if isinstance(payload, dict):
            file_name = payload.get("file_path", "")
        else:
            file_name = str(payload)
        self._discovered_files += 1
        self._current_file = file_name
        self._emit_progress(stage="Scanning", current_file=file_name, status="Scanning")
        
    def _on_val_started(self, payload):
        file_name = "Unknown"
        if hasattr(payload, "file_name"):
            file_name = payload.file_name
        elif hasattr(payload, "file_path"):
            file_name = str(payload.file_path)
        elif isinstance(payload, dict):
            file_name = str(payload.get("task_id", "Unknown"))
        self._current_file = str(file_name)
        self._emit_progress(stage="Validating", current_file=self._current_file, status="Processing")
        
    def _on_val_failed(self, payload):
        if hasattr(payload, "task_id"):
            self._emit_progress(stage="Failed", current_file=str(payload.task_id), status="Validation Failed")

    def _on_val_skipped(self, payload):
        self._emit_progress(stage="Validating", current_file=str(payload), status="Skipped")
        
    def _on_val_completed(self, payload):
        # payload is a ValidationResult object
        if not payload:
            return

        self._results.append(payload)
        self._processed_files += 1
        self.result_added.emit(payload)
        elapsed = max(time.time() - self._start_time, 0.0)
        stats = self._compute_stats(self._results, elapsed)
        self.dashboard_updated.emit(stats)
        current_file = getattr(getattr(payload, "task", None), "file_name", self._current_file)
        self._emit_progress(stage="Validating", current_file=str(current_file), status="Processing")
        
    def _on_shutdown(self, payload):
        self._emit_progress(stage="Completed", current_file=str(payload), status="Validation Completed Successfully", force_progress=100.0)

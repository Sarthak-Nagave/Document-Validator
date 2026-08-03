"""Scan service."""
from pathlib import Path
import os
import logging
from typing import Generator
from interfaces.scanner import IScanner
from domain.entities.validation_task import ValidationTask
from app.execution_context import ExecutionContext
from events.event_bus import EventBus
from events.event_types import EventType

class ScanService(IScanner):
    def __init__(self, context: ExecutionContext, event_bus: EventBus):
        self.context = context
        self.event_bus = event_bus
        self.config = context.config.scanning

    def scan(self, root_path: str) -> Generator[ValidationTask, None, None]:
        root = Path(root_path)
        if not root.exists():
            logging.error(f"Root path does not exist: {root}")
            return

        self.event_bus.publish(EventType.SCAN_STARTED, root_path)
        
        for task in self._scan_recursive(root, root):
            yield task

    def _scan_recursive(self, current_dir: Path, root_dir: Path) -> Generator[ValidationTask, None, None]:
        self.context.metrics.folders_visited += 1
        self.event_bus.publish(EventType.FOLDER_DISCOVERED, str(current_dir))

        try:
            for entry in current_dir.iterdir():
                if entry.is_dir():
                    if entry.name in self.config.ignored_folders or (self.config.ignore_hidden and entry.name.startswith('.')):
                        self.context.metrics.skipped_folders += 1
                        self.event_bus.publish(EventType.FOLDER_SKIPPED, str(entry))
                        continue
                    yield from self._scan_recursive(entry, root_dir)
                else:
                    self.context.metrics.files_visited += 1
                    if self.config.ignore_hidden and entry.name.startswith('.'):
                        self.context.metrics.skipped_files += 1
                        continue
                    
                    ext = entry.suffix.lower()
                    if ext in self.config.ignored_extensions:
                        self.context.metrics.skipped_files += 1
                        continue
                        
                    if ext not in self.config.supported_extensions:
                        self.context.metrics.unsupported_files += 1
                        # Continue processing unsupported to log or just skip? User said unsupported files count.
                    else:
                        if ext == ".pdf":
                            self.context.metrics.pdf_files += 1
                        elif ext == ".xlsx":
                            self.context.metrics.excel_files += 1
                            
                    self.context.metrics.files_scanned += 1
                    self.event_bus.publish(EventType.FILE_DISCOVERED, str(entry))
                    
                    rel_path_obj = entry.relative_to(root_dir)
                    root_group_name = rel_path_obj.parts[0] if len(rel_path_obj.parts) > 0 else "Unknown"

                    stat = entry.stat()
                    task = ValidationTask(
                        file_path=entry.absolute(),
                        relative_path=str(rel_path_obj),
                        file_name=entry.name,
                        extension=ext,
                        root_group=root_group_name,
                        file_size=stat.st_size,
                        created_time=stat.st_ctime,
                        modified_time=stat.st_mtime
                    )
                    self.context.metrics.validation_tasks_created += 1
                    yield task
        except PermissionError:
            self.context.metrics.errors += 1
            logging.warning(f"Permission denied accessing: {current_dir}")
        except Exception as e:
            self.context.metrics.errors += 1
            logging.error(f"Error accessing {current_dir}: {e}")

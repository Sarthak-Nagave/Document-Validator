"""Dependency container for assembling DVE runtime services."""

from __future__ import annotations

from pathlib import Path
import logging

from app.execution_context import ExecutionContext
from config.config_loader import ConfigLoader
from core.dispatcher import Dispatcher
from core.engine import CoreEngine
from core.lifecycle import LifecycleManager
from core.pipeline import ValidationPipeline
from crypto.engine import CryptoEngine
from crypto.key_manager import KeyManager
from events.event_bus import EventBus
from factories.report_factory import ReportFactory
from factories.service_factory import ServiceFactory
from infrastructure.resources.resource_manager import ResourceManager
from plugins.loader import PluginLoader
from plugins.registry import PluginRegistry
from services.configuration_service import ConfigurationService
from factories.validator_factory import ValidatorFactory
from services.scan_service import ScanService
from services.validation_orchestrator import ValidationOrchestrator
from version.version_manager import VersionManager
from validators.excel_validator import ExcelValidator
from validators.pdf_validator import PDFValidator


logger = logging.getLogger(__name__)


class DependencyContainer:
	"""Composition root for all non-UI dependencies."""

	def __init__(self, root_path: Path) -> None:
		self.root_path = root_path
		self.config = ConfigLoader(root_path / "config" / "config.json").load()
		self.configuration_service = ConfigurationService(self.config)
		self.resource_manager = ResourceManager(root_path)
		self.version_manager = VersionManager()
		self.context = ExecutionContext(config=self.config)
		self.event_bus = EventBus()

		self.key_manager = KeyManager(self.config.excel, root_path)
		self.crypto_engine = CryptoEngine()

		self.validator_factory = ValidatorFactory()
		self._register_validators()

		self.scanner = ScanService(self.context, self.event_bus)
		self.dispatcher = Dispatcher(self.validator_factory, self.event_bus)
		self.orchestrator = ValidationOrchestrator(self.scanner, self.dispatcher)
		self.pipeline = ValidationPipeline(self.orchestrator)
		self.lifecycle = LifecycleManager()

		report_manager = ReportFactory.create()
		self.report_service = ServiceFactory.create_report_service(
			report_manager, output_root=root_path / "output"
		)
		self.engine = CoreEngine(self.pipeline, self.report_service, self.lifecycle)

		self.plugin_registry = PluginRegistry()
		self.plugin_loader = PluginLoader(root_path / "plugins", self.plugin_registry)
		self.plugin_loader.load()
		self._activate_plugins()

		logger.info("Dependency container initialized")

	def _activate_plugins(self) -> None:
		"""Invoke plugin registration against this container."""
		for plugin in self.plugin_registry.all():
			try:
				plugin.register(self)
				logger.info("Activated plugin: %s", plugin.name)
			except Exception as exc:  # pragma: no cover - runtime safety
				logger.exception("Plugin activation failed for %s: %s", plugin.name, exc)

	def _register_validators(self) -> None:
		pdf_validator = PDFValidator(self.event_bus, self.config.pdf)
		excel_validator = ExcelValidator(
			event_bus=self.event_bus,
			excel_config=self.config.excel,
			crypto_config=self.config.crypto,
			validation_policy=self.config.validation_policy,
			key_manager=self.key_manager,
			crypto_engine=self.crypto_engine,
		)
		self.validator_factory.register(".pdf", pdf_validator)
		self.validator_factory.register(".xlsx", excel_validator)


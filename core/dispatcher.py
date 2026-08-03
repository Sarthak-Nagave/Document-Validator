"""Task dispatcher."""
from domain.entities.validation_task import ValidationTask
from domain.value_objects.validation_result import ValidationResult
from factories.validator_factory import ValidatorFactory
from events.event_bus import EventBus
from events.event_types import EventType
import time
import logging

class Dispatcher:
    def __init__(self, factory: ValidatorFactory, event_bus: EventBus):
        self.factory = factory
        self.event_bus = event_bus

    def dispatch(self, task: ValidationTask) -> ValidationResult:
        validator = self.factory.get_validator(task.extension)
        if not validator:
            logging.info(f"No validator found for {task.extension}, skipping.")
            self.event_bus.publish(EventType.VALIDATION_SKIPPED, task)
            return None
            
        self.event_bus.publish(EventType.VALIDATION_STARTED, task)
        result = validator.validate(task)
        self.event_bus.publish(EventType.VALIDATION_COMPLETED, result)
        
        return result

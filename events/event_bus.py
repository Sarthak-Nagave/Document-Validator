"""Thread-safe in-process event bus for DVE components."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from threading import RLock
from typing import Any, TypeAlias
import logging


logger = logging.getLogger(__name__)

EventType: TypeAlias = Any
EventPayload: TypeAlias = Any
EventHandler: TypeAlias = Callable[[EventPayload], None]


class EventBus:
	"""Synchronous, thread-safe event bus used by core services and GUI worker."""

	def __init__(self) -> None:
		self._subscribers: dict[EventType, list[EventHandler]] = defaultdict(list)
		self._lock = RLock()

	def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
		"""Register a handler for an event type."""
		with self._lock:
			if handler not in self._subscribers[event_type]:
				self._subscribers[event_type].append(handler)
				logger.debug("Subscribed handler=%s to event=%s", handler, event_type)

	def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
		"""Remove a handler from an event type subscription list."""
		with self._lock:
			handlers = self._subscribers.get(event_type)
			if not handlers:
				return
			if handler in handlers:
				handlers.remove(handler)
				logger.debug("Unsubscribed handler=%s from event=%s", handler, event_type)

	def has_subscribers(self, event_type: EventType) -> bool:
		"""Return True when an event has at least one subscriber."""
		with self._lock:
			return bool(self._subscribers.get(event_type))

	def publish(self, event_type: EventType, payload: EventPayload) -> None:
		"""Publish an event to all subscribers while isolating handler failures."""
		with self._lock:
			handlers = list(self._subscribers.get(event_type, []))

		logger.debug("Publishing event=%s to subscribers=%s", event_type, len(handlers))
		for handler in handlers:
			try:
				handler(payload)
			except Exception as exc:  # pragma: no cover - defensive runtime safety
				logger.exception("Event handler failure for %s: %s", event_type, exc)


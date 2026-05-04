from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers[topic].append(handler)

    def publish(self, topic: str, payload: dict[str, Any] | None = None) -> None:
        data = payload or {}
        for handler in list(self._subscribers.get(topic, ())):
            handler(data)

    def clear(self) -> None:
        self._subscribers.clear()

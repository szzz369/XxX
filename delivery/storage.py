from __future__ import annotations

from typing import Dict, Iterable, Optional

from delivery.models import DeliveryOrder


class DeliveryOrderRepository:
    def __init__(self) -> None:
        self._orders: Dict[str, DeliveryOrder] = {}

    def upsert(self, order: DeliveryOrder) -> None:
        self._orders[order.third_order_id] = order

    def get(self, third_order_id: str) -> Optional[DeliveryOrder]:
        return self._orders.get(third_order_id)

    def all(self) -> Iterable[DeliveryOrder]:
        return self._orders.values()

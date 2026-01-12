from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DeliveryOrderRequest:
    order_id: str
    pickup_address: str
    dropoff_address: str
    recipient_name: str
    recipient_phone: str
    fee: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class DeliveryOrderResponse:
    provider: str
    third_order_id: str
    status: str
    raw: Dict[str, Any]


class DeliveryAdapter(ABC):
    provider: str

    @abstractmethod
    def create_order(self, payload: DeliveryOrderRequest) -> DeliveryOrderResponse:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, third_order_id: str, reason: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def query_status(self, third_order_id: str) -> Dict[str, Any]:
        raise NotImplementedError

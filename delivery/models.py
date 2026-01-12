from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CourierInfo:
    name: str
    phone: str
    vehicle_type: Optional[str] = None


@dataclass
class DeliveryOrder:
    provider: str
    third_order_id: str
    delivery_status: str
    fee: float
    courier_info: Optional[CourierInfo] = None
    raw_payload: Optional[Dict[str, Any]] = None

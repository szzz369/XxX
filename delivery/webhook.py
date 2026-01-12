from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from delivery.models import CourierInfo, DeliveryOrder
from delivery.storage import DeliveryOrderRepository


@dataclass(frozen=True)
class WebhookResult:
    accepted: bool
    message: str
    order: Optional[DeliveryOrder] = None


class WebhookProcessor:
    def __init__(
        self,
        repository: DeliveryOrderRepository,
        provider_secrets: Dict[str, str],
    ) -> None:
        self._repository = repository
        self._provider_secrets = provider_secrets
        self._seen_events: Set[str] = set()

    def handle(self, payload: Dict[str, Any]) -> WebhookResult:
        provider = payload.get("provider")
        event_id = payload.get("event_id")
        signature = payload.get("signature")
        if not provider or not event_id or not signature:
            return WebhookResult(accepted=False, message="missing required fields")

        if event_id in self._seen_events:
            return WebhookResult(accepted=True, message="duplicate event ignored")

        secret = self._provider_secrets.get(provider)
        if not secret:
            return WebhookResult(accepted=False, message="unknown provider")

        if not self._verify_signature(payload, secret):
            return WebhookResult(accepted=False, message="invalid signature")

        third_order_id = payload.get("third_order_id")
        status = payload.get("delivery_status")
        fee = payload.get("fee", 0.0)
        courier_info = payload.get("courier_info") or {}
        if not third_order_id or not status:
            return WebhookResult(accepted=False, message="missing order fields")

        courier = None
        if courier_info:
            courier = CourierInfo(
                name=courier_info.get("name", ""),
                phone=courier_info.get("phone", ""),
                vehicle_type=courier_info.get("vehicle_type"),
            )

        order = DeliveryOrder(
            provider=provider,
            third_order_id=third_order_id,
            delivery_status=status,
            fee=float(fee),
            courier_info=courier,
            raw_payload=payload,
        )
        self._repository.upsert(order)
        self._seen_events.add(event_id)
        return WebhookResult(accepted=True, message="status updated", order=order)

    def _verify_signature(self, payload: Dict[str, Any], secret: str) -> bool:
        payload_copy = {k: v for k, v in payload.items() if k != "signature"}
        message = "&".join(f"{k}={payload_copy[k]}" for k in sorted(payload_copy))
        digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, payload.get("signature", ""))

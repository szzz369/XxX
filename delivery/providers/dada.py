from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict

from delivery.adapter import DeliveryAdapter, DeliveryOrderRequest, DeliveryOrderResponse


class DadaAdapter(DeliveryAdapter):
    provider = "dada"

    def __init__(self, app_key: str, app_secret: str) -> None:
        self._app_key = app_key
        self._app_secret = app_secret

    def create_order(self, payload: DeliveryOrderRequest) -> DeliveryOrderResponse:
        request = {
            "order_id": payload.order_id,
            "pickup_address": payload.pickup_address,
            "dropoff_address": payload.dropoff_address,
            "recipient_name": payload.recipient_name,
            "recipient_phone": payload.recipient_phone,
            "fee": payload.fee,
            "metadata": payload.metadata or {},
            "timestamp": int(time.time()),
        }
        request["signature"] = self._sign(request)
        third_order_id = f"dada-{payload.order_id}"
        return DeliveryOrderResponse(
            provider=self.provider,
            third_order_id=third_order_id,
            status="created",
            raw=request,
        )

    def cancel_order(self, third_order_id: str, reason: str) -> Dict[str, Any]:
        request = {
            "third_order_id": third_order_id,
            "reason": reason,
            "timestamp": int(time.time()),
        }
        request["signature"] = self._sign(request)
        return {"provider": self.provider, "result": "cancelled", "raw": request}

    def query_status(self, third_order_id: str) -> Dict[str, Any]:
        request = {"third_order_id": third_order_id, "timestamp": int(time.time())}
        request["signature"] = self._sign(request)
        return {"provider": self.provider, "status": "in_transit", "raw": request}

    def _sign(self, payload: Dict[str, Any]) -> str:
        message = "&".join(f"{k}={payload[k]}" for k in sorted(payload))
        digest = hmac.new(self._app_secret.encode(), message.encode(), hashlib.sha256)
        return digest.hexdigest()

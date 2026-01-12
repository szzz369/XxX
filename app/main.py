from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, PositiveInt

app = FastAPI(title="Order & Delivery Service")

PAYMENT_SECRET = b"payment-secret"
DELIVERY_SECRET = b"delivery-secret"


@dataclass
class Order:
    order_id: str
    items: List["OrderItem"]
    total_price: int
    zone: str
    status: Literal["pending", "paid", "completed"] = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Payment:
    prepay_id: str
    order_id: str
    amount: int
    transaction_id: str | None = None
    status: Literal["created", "paid"] = "created"


@dataclass
class Delivery:
    delivery_id: str
    order_id: str
    address: str
    status: Literal["created", "in_transit", "delivered"] = "created"
    tracks: List[str] = field(default_factory=list)


class OrderItem(BaseModel):
    sku: str
    quantity: PositiveInt


class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    total_price: int = Field(ge=0)
    zone: str


class CreateOrderResponse(BaseModel):
    order_id: str
    status: str


class PrepayRequest(BaseModel):
    order_id: str
    amount: int = Field(ge=0)


class PrepayResponse(BaseModel):
    prepay_id: str
    status: str


class PaymentCallbackRequest(BaseModel):
    prepay_id: str
    transaction_id: str
    signature: str


class CreateDeliveryRequest(BaseModel):
    order_id: str
    address: str


class CreateDeliveryResponse(BaseModel):
    delivery_id: str
    status: str


class DeliveryCallbackRequest(BaseModel):
    delivery_id: str
    status: Literal["delivered"]
    signature: str


INVENTORY: Dict[str, int] = {"sku-1": 10, "sku-2": 5}
PRICES: Dict[str, int] = {"sku-1": 100, "sku-2": 240}
DELIVERY_ZONES = {"zone-a", "zone-b"}

ORDERS: Dict[str, Order] = {}
PAYMENTS: Dict[str, Payment] = {}
DELIVERIES: Dict[str, Delivery] = {}
PROCESSED_TRANSACTIONS: set[str] = set()


def compute_signature(secret: bytes, payload: str) -> str:
    digest = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def validate_inventory(items: List[OrderItem]) -> None:
    for item in items:
        available = INVENTORY.get(item.sku, 0)
        if item.quantity > available:
            raise HTTPException(status_code=400, detail=f"insufficient stock for {item.sku}")


def validate_price(items: List[OrderItem], total_price: int) -> None:
    calculated = 0
    for item in items:
        price = PRICES.get(item.sku)
        if price is None:
            raise HTTPException(status_code=400, detail=f"price missing for {item.sku}")
        calculated += price * item.quantity
    if calculated != total_price:
        raise HTTPException(status_code=400, detail="total_price mismatch")


def validate_zone(zone: str) -> None:
    if zone not in DELIVERY_ZONES:
        raise HTTPException(status_code=400, detail="delivery zone not supported")


@app.post("/orders", response_model=CreateOrderResponse)
def create_order(payload: CreateOrderRequest) -> CreateOrderResponse:
    validate_inventory(payload.items)
    validate_price(payload.items, payload.total_price)
    validate_zone(payload.zone)

    order_id = str(uuid.uuid4())
    ORDERS[order_id] = Order(
        order_id=order_id,
        items=payload.items,
        total_price=payload.total_price,
        zone=payload.zone,
    )
    return CreateOrderResponse(order_id=order_id, status="pending")


@app.post("/payments/prepay", response_model=PrepayResponse)
def create_prepay(payload: PrepayRequest) -> PrepayResponse:
    order = ORDERS.get(payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="order not payable")
    if payload.amount != order.total_price:
        raise HTTPException(status_code=400, detail="amount mismatch")

    prepay_id = str(uuid.uuid4())
    PAYMENTS[prepay_id] = Payment(prepay_id=prepay_id, order_id=order.order_id, amount=payload.amount)
    return PrepayResponse(prepay_id=prepay_id, status="created")


@app.post("/payments/callback")
def payment_callback(payload: PaymentCallbackRequest) -> dict:
    payment = PAYMENTS.get(payload.prepay_id)
    if not payment:
        raise HTTPException(status_code=404, detail="prepay not found")

    expected = compute_signature(PAYMENT_SECRET, f"{payload.prepay_id}:{payload.transaction_id}")
    if not hmac.compare_digest(expected, payload.signature):
        raise HTTPException(status_code=400, detail="invalid signature")

    if payload.transaction_id in PROCESSED_TRANSACTIONS:
        return {"status": "duplicate"}

    order = ORDERS.get(payment.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")

    payment.transaction_id = payload.transaction_id
    payment.status = "paid"
    order.status = "paid"
    PROCESSED_TRANSACTIONS.add(payload.transaction_id)

    return {"status": "ok"}


@app.post("/deliveries", response_model=CreateDeliveryResponse)
def create_delivery(payload: CreateDeliveryRequest) -> CreateDeliveryResponse:
    order = ORDERS.get(payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail="order not paid")

    delivery_id = str(uuid.uuid4())
    delivery = Delivery(delivery_id=delivery_id, order_id=order.order_id, address=payload.address)
    delivery.status = "in_transit"
    delivery.tracks.append(f"{datetime.now(timezone.utc).isoformat()} created")
    DELIVERIES[delivery_id] = delivery
    return CreateDeliveryResponse(delivery_id=delivery_id, status=delivery.status)


@app.post("/deliveries/callback")
def delivery_callback(payload: DeliveryCallbackRequest) -> dict:
    delivery = DELIVERIES.get(payload.delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="delivery not found")

    expected = compute_signature(DELIVERY_SECRET, payload.delivery_id)
    if not hmac.compare_digest(expected, payload.signature):
        raise HTTPException(status_code=400, detail="invalid signature")

    if delivery.status == "delivered":
        return {"status": "duplicate"}

    delivery.status = "delivered"
    delivery.tracks.append(f"{datetime.now(timezone.utc).isoformat()} delivered")

    order = ORDERS.get(delivery.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    order.status = "completed"

    return {"status": "ok"}

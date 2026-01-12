from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Set

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field, PositiveInt

app = FastAPI(title="Order & Delivery Service")


DELIVERY_CITIES = {"Shanghai", "Beijing", "Shenzhen"}
PAYMENT_SIGNATURE_SECRET = b"super-secret"


@dataclass
class InventoryItem:
    sku: str
    price: int
    stock: int


@dataclass
class Order:
    order_id: str
    items: List["OrderItem"]
    total_amount: int
    city: str
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Payment:
    prepay_id: str
    order_id: str
    status: str
    amount: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Delivery:
    delivery_id: str
    order_id: str
    status: str
    tracks: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


INVENTORY: Dict[str, InventoryItem] = {
    "SKU-001": InventoryItem(sku="SKU-001", price=1999, stock=50),
    "SKU-002": InventoryItem(sku="SKU-002", price=3999, stock=30),
}
ORDERS: Dict[str, Order] = {}
PAYMENTS: Dict[str, Payment] = {}
DELIVERIES: Dict[str, Delivery] = {}
PAYMENT_EVENTS: Set[str] = set()


class Address(BaseModel):
    city: str = Field(..., description="City name used for delivery range check")
    detail: str


class OrderItem(BaseModel):
    sku: str
    quantity: PositiveInt
    unit_price: PositiveInt


class OrderRequest(BaseModel):
    items: List[OrderItem]
    address: Address


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: int


class PrepayRequest(BaseModel):
    order_id: str


class PrepayResponse(BaseModel):
    prepay_id: str
    order_id: str
    status: str


class PaymentCallback(BaseModel):
    event_id: str
    prepay_id: str
    amount: PositiveInt
    status: str = Field(..., description="PAID or FAILED")


class DeliveryRequest(BaseModel):
    order_id: str
    carrier: str


class DeliveryResponse(BaseModel):
    delivery_id: str
    status: str
    tracks: List[str]


class DeliveryCallback(BaseModel):
    delivery_id: str
    status: str = Field(..., description="DELIVERED")
    track: str


def _validate_delivery_range(city: str) -> None:
    if city not in DELIVERY_CITIES:
        raise HTTPException(status_code=400, detail="Delivery city out of range")


def _validate_inventory(items: List[OrderItem]) -> int:
    total_amount = 0
    for item in items:
        inventory_item = INVENTORY.get(item.sku)
        if not inventory_item:
            raise HTTPException(status_code=400, detail=f"Unknown SKU: {item.sku}")
        if inventory_item.price != item.unit_price:
            raise HTTPException(status_code=400, detail=f"Price mismatch for {item.sku}")
        if inventory_item.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.sku}")
        total_amount += item.unit_price * item.quantity
    return total_amount


def _reserve_stock(items: List[OrderItem]) -> None:
    for item in items:
        INVENTORY[item.sku].stock -= item.quantity


def _sign_payload(payload: bytes) -> str:
    digest = hmac.new(PAYMENT_SIGNATURE_SECRET, payload, hashlib.sha256).hexdigest()
    return digest


@app.post("/orders", response_model=OrderResponse)
def create_order(request: OrderRequest) -> OrderResponse:
    _validate_delivery_range(request.address.city)
    total_amount = _validate_inventory(request.items)
    _reserve_stock(request.items)
    order_id = uuid.uuid4().hex
    ORDERS[order_id] = Order(
        order_id=order_id,
        items=request.items,
        total_amount=total_amount,
        city=request.address.city,
        status="PENDING_PAYMENT",
    )
    return OrderResponse(order_id=order_id, status="PENDING_PAYMENT", total_amount=total_amount)


@app.post("/payments/prepay", response_model=PrepayResponse)
def create_prepay(request: PrepayRequest) -> PrepayResponse:
    order = ORDERS.get(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "PENDING_PAYMENT":
        raise HTTPException(status_code=400, detail="Order is not awaiting payment")
    prepay_id = uuid.uuid4().hex
    PAYMENTS[prepay_id] = Payment(
        prepay_id=prepay_id,
        order_id=order.order_id,
        status="PENDING",
        amount=order.total_amount,
    )
    return PrepayResponse(prepay_id=prepay_id, order_id=order.order_id, status="PENDING")


@app.post("/payments/callback")
async def payment_callback(
    request: Request,
    payload: PaymentCallback,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> dict:
    raw_body = await request.body()
    if not x_signature or _sign_payload(raw_body) != x_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    if payload.event_id in PAYMENT_EVENTS:
        return {"status": "duplicate_ignored"}
    PAYMENT_EVENTS.add(payload.event_id)
    payment = PAYMENTS.get(payload.prepay_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payload.amount != payment.amount:
        raise HTTPException(status_code=400, detail="Amount mismatch")
    if payload.status == "PAID":
        payment.status = "PAID"
        order = ORDERS[payment.order_id]
        order.status = "PAID"
    else:
        payment.status = "FAILED"
        order = ORDERS[payment.order_id]
        order.status = "PAYMENT_FAILED"
    return {"status": "processed"}


@app.post("/deliveries", response_model=DeliveryResponse)
def create_delivery(request: DeliveryRequest) -> DeliveryResponse:
    order = ORDERS.get(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "PAID":
        raise HTTPException(status_code=400, detail="Order is not ready for delivery")
    delivery_id = uuid.uuid4().hex
    tracks = [f"{request.carrier} shipment created"]
    delivery = Delivery(
        delivery_id=delivery_id,
        order_id=order.order_id,
        status="IN_TRANSIT",
        tracks=tracks,
    )
    DELIVERIES[delivery_id] = delivery
    order.status = "SHIPPING"
    return DeliveryResponse(delivery_id=delivery_id, status=delivery.status, tracks=tracks)


@app.post("/deliveries/callback")
def delivery_callback(payload: DeliveryCallback) -> dict:
    delivery = DELIVERIES.get(payload.delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    delivery.tracks.append(payload.track)
    if payload.status == "DELIVERED":
        delivery.status = "DELIVERED"
        order = ORDERS[delivery.order_id]
        order.status = "COMPLETED"
    return {"status": "updated"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

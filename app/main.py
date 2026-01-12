from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Delivery & Membership Service")


class StoreInfo(BaseModel):
    store_id: str
    name: str
    address: str


class DeliveryProviderConfig(BaseModel):
    provider_id: str
    merchant_id: str
    merchant_name: str
    signing_key: str
    stores: List[StoreInfo] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MemberLevel(BaseModel):
    level_id: str
    name: str
    threshold: int
    benefits: List[str] = Field(default_factory=list)
    upgrade_rule: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Member(BaseModel):
    member_id: str
    name: str
    level_id: str
    joined_at: date = Field(default_factory=date.today)


class DeliveryOrder(BaseModel):
    order_id: str
    provider_id: str
    member_id: str
    total_amount: float
    status: str = "created"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    canceled_at: Optional[datetime] = None
    exception_reason: Optional[str] = None


class DeliveryOrderCreate(BaseModel):
    provider_id: str
    member_id: str
    total_amount: float


class DeliveryOrderUpdate(BaseModel):
    status: Optional[str] = None
    exception_reason: Optional[str] = None


class MemberCreate(BaseModel):
    name: str
    level_id: str


provider_configs: Dict[str, DeliveryProviderConfig] = {}
member_levels: Dict[str, MemberLevel] = {}
members: Dict[str, Member] = {}
orders: Dict[str, DeliveryOrder] = {}


@app.get("/providers", response_model=List[DeliveryProviderConfig])
def list_providers() -> List[DeliveryProviderConfig]:
    return list(provider_configs.values())


@app.get("/providers/{provider_id}", response_model=DeliveryProviderConfig)
def get_provider(provider_id: str) -> DeliveryProviderConfig:
    provider = provider_configs.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@app.post("/providers", response_model=DeliveryProviderConfig)
def create_provider(config: DeliveryProviderConfig) -> DeliveryProviderConfig:
    if config.provider_id in provider_configs:
        raise HTTPException(status_code=409, detail="Provider already exists")
    provider_configs[config.provider_id] = config
    return config


@app.put("/providers/{provider_id}", response_model=DeliveryProviderConfig)
def upsert_provider(provider_id: str, config: DeliveryProviderConfig) -> DeliveryProviderConfig:
    if provider_id != config.provider_id:
        raise HTTPException(status_code=400, detail="Provider ID mismatch")
    config.updated_at = datetime.utcnow()
    provider_configs[provider_id] = config
    return config


@app.get("/member-levels", response_model=List[MemberLevel])
def list_member_levels() -> List[MemberLevel]:
    return list(member_levels.values())


@app.get("/member-levels/{level_id}", response_model=MemberLevel)
def get_member_level(level_id: str) -> MemberLevel:
    level = member_levels.get(level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Member level not found")
    return level


@app.post("/member-levels", response_model=MemberLevel)
def create_member_level(level: MemberLevel) -> MemberLevel:
    if level.level_id in member_levels:
        raise HTTPException(status_code=409, detail="Member level already exists")
    member_levels[level.level_id] = level
    return level


@app.put("/member-levels/{level_id}", response_model=MemberLevel)
def upsert_member_level(level_id: str, level: MemberLevel) -> MemberLevel:
    if level_id != level.level_id:
        raise HTTPException(status_code=400, detail="Level ID mismatch")
    level.updated_at = datetime.utcnow()
    member_levels[level_id] = level
    return level


@app.post("/members", response_model=Member)
def create_member(payload: MemberCreate) -> Member:
    if payload.level_id not in member_levels:
        raise HTTPException(status_code=404, detail="Member level not found")
    member_id = str(uuid4())
    member = Member(member_id=member_id, name=payload.name, level_id=payload.level_id)
    members[member_id] = member
    return member


@app.get("/members", response_model=List[Member])
def list_members() -> List[Member]:
    return list(members.values())


@app.post("/orders", response_model=DeliveryOrder)
def create_order(payload: DeliveryOrderCreate) -> DeliveryOrder:
    if payload.provider_id not in provider_configs:
        raise HTTPException(status_code=404, detail="Provider not found")
    if payload.member_id not in members:
        raise HTTPException(status_code=404, detail="Member not found")
    order_id = str(uuid4())
    order = DeliveryOrder(
        order_id=order_id,
        provider_id=payload.provider_id,
        member_id=payload.member_id,
        total_amount=payload.total_amount,
    )
    orders[order_id] = order
    return order


@app.get("/orders", response_model=List[DeliveryOrder])
def query_orders(
    status: Optional[str] = None,
    provider_id: Optional[str] = None,
    member_id: Optional[str] = None,
) -> List[DeliveryOrder]:
    results = list(orders.values())
    if status:
        results = [order for order in results if order.status == status]
    if provider_id:
        results = [order for order in results if order.provider_id == provider_id]
    if member_id:
        results = [order for order in results if order.member_id == member_id]
    return results


@app.get("/orders/{order_id}", response_model=DeliveryOrder)
def get_order(order_id: str) -> DeliveryOrder:
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders/{order_id}/cancel", response_model=DeliveryOrder)
def cancel_order(order_id: str) -> DeliveryOrder:
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "canceled":
        return order
    if order.status not in {"created", "in_progress"}:
        raise HTTPException(status_code=400, detail="Order cannot be canceled")
    order.status = "canceled"
    order.canceled_at = datetime.utcnow()
    return order


@app.post("/orders/{order_id}/exception", response_model=DeliveryOrder)
def mark_order_exception(order_id: str, payload: DeliveryOrderUpdate) -> DeliveryOrder:
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status or "exception"
    order.exception_reason = payload.exception_reason or "Unspecified exception"
    return order


@app.get("/reports/members/level-distribution")
def member_level_distribution() -> Dict[str, int]:
    distribution: Dict[str, int] = {}
    for member in members.values():
        distribution[member.level_id] = distribution.get(member.level_id, 0) + 1
    return distribution


@app.get("/reports/members/upgrade-trends")
def member_upgrade_trends() -> Dict[str, int]:
    trends: Dict[str, int] = {}
    for level in member_levels.values():
        trends[level.level_id] = 0
    for member in members.values():
        trends[member.level_id] = trends.get(member.level_id, 0) + 1
    return trends


@app.get("/reports/members/revenue-contribution")
def member_revenue_contribution() -> Dict[str, float]:
    revenue: Dict[str, float] = {}
    for order in orders.values():
        if order.status == "canceled":
            continue
        member = members.get(order.member_id)
        if not member:
            continue
        revenue[member.level_id] = revenue.get(member.level_id, 0.0) + order.total_amount
    return revenue

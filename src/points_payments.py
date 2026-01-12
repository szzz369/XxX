from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class PaymentMethod(str, Enum):
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_CARD = "bank_card"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class PointsConfig:
    ratio: float
    max_deduction: float


@dataclass
class PointsWallet:
    available: int
    frozen: int = 0

    def freeze(self, points: int) -> None:
        if points < 0:
            raise ValueError("points_to_freeze must be non-negative")
        if points > self.available:
            raise ValueError("insufficient points")
        self.available -= points
        self.frozen += points

    def deduct_frozen(self, points: int) -> None:
        if points < 0:
            raise ValueError("points_to_deduct must be non-negative")
        if points > self.frozen:
            raise ValueError("insufficient frozen points")
        self.frozen -= points

    def rollback(self, points: int) -> None:
        if points < 0:
            raise ValueError("points_to_rollback must be non-negative")
        if points > self.frozen:
            raise ValueError("insufficient frozen points")
        self.frozen -= points
        self.available += points


@dataclass
class PaymentOrder:
    order_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING

    def mark_success(self) -> None:
        self.status = PaymentStatus.SUCCESS

    def mark_failed(self) -> None:
        self.status = PaymentStatus.FAILED


@dataclass
class Order:
    order_id: str
    total_amount: float
    points_used: int
    cash_amount: float
    payment_method: Optional[PaymentMethod]
    payment_order: Optional[PaymentOrder] = None
    payment_status: PaymentStatus = PaymentStatus.PENDING


@dataclass
class PointsPaymentService:
    config: PointsConfig
    wallets: Dict[str, PointsWallet] = field(default_factory=dict)
    orders: Dict[str, Order] = field(default_factory=dict)
    payments: Dict[str, PaymentOrder] = field(default_factory=dict)

    def register_wallet(self, customer_id: str, points: int) -> None:
        if points < 0:
            raise ValueError("points must be non-negative")
        self.wallets[customer_id] = PointsWallet(available=points)

    def create_order(
        self,
        customer_id: str,
        order_id: str,
        total_amount: float,
        points_to_use: int,
        payment_method: Optional[PaymentMethod],
    ) -> Order:
        if total_amount <= 0:
            raise ValueError("total_amount must be positive")
        if points_to_use < 0:
            raise ValueError("points_to_use must be non-negative")
        if payment_method is None and points_to_use <= 0:
            raise ValueError("payment_method required when not using points")
        wallet = self._get_wallet(customer_id)
        max_points_value = self.config.max_deduction
        points_value = points_to_use * self.config.ratio
        if points_value > max_points_value:
            raise ValueError("points exceed max deduction")
        if points_value > total_amount:
            raise ValueError("points exceed total amount")

        if points_to_use:
            wallet.freeze(points_to_use)

        cash_amount = round(total_amount - points_value, 2)
        payment_order = None
        if cash_amount > 0:
            if payment_method is None:
                raise ValueError("payment_method required for cash amount")
            payment_order = PaymentOrder(
                order_id=order_id,
                amount=cash_amount,
                method=payment_method,
            )
            self.payments[order_id] = payment_order

        order = Order(
            order_id=order_id,
            total_amount=total_amount,
            points_used=points_to_use,
            cash_amount=cash_amount,
            payment_method=payment_method,
            payment_order=payment_order,
        )
        self.orders[order_id] = order
        return order

    def handle_payment_success(self, customer_id: str, order_id: str) -> None:
        order = self._get_order(order_id)
        if order.payment_order:
            order.payment_order.mark_success()
        order.payment_status = PaymentStatus.SUCCESS
        if order.points_used:
            wallet = self._get_wallet(customer_id)
            wallet.deduct_frozen(order.points_used)

    def handle_payment_failure(self, customer_id: str, order_id: str) -> None:
        order = self._get_order(order_id)
        if order.payment_order:
            order.payment_order.mark_failed()
        order.payment_status = PaymentStatus.FAILED
        if order.points_used:
            wallet = self._get_wallet(customer_id)
            wallet.rollback(order.points_used)

    def _get_wallet(self, customer_id: str) -> PointsWallet:
        if customer_id not in self.wallets:
            raise KeyError("wallet not found")
        return self.wallets[customer_id]

    def _get_order(self, order_id: str) -> Order:
        if order_id not in self.orders:
            raise KeyError("order not found")
        return self.orders[order_id]

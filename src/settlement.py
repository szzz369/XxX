from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import Optional


class DiscountType(Enum):
    RATE = "rate"
    AMOUNT = "amount"


class PaymentMode(Enum):
    FULL_POINTS = "full_points"
    PARTIAL_POINTS = "partial_points"
    CASH = "cash"


@dataclass(frozen=True)
class Discount:
    discount_type: DiscountType
    value: Decimal

    def apply(self, amount: Decimal) -> Decimal:
        if self.discount_type == DiscountType.RATE:
            return (amount * (Decimal("1") - self.value)).quantize(Decimal("0.01"))
        return max(Decimal("0"), amount - self.value).quantize(Decimal("0.01"))


@dataclass(frozen=True)
class Coupon:
    amount: Decimal


@dataclass(frozen=True)
class PointsPolicy:
    points_to_currency_rate: Decimal
    max_points: int
    max_deduct_amount: Decimal


@dataclass(frozen=True)
class ShippingPolicy:
    free_shipping: bool = False
    discount: Optional[Discount] = None


@dataclass(frozen=True)
class SettlementInput:
    original_price: Decimal
    member_discount: Optional[Discount]
    coupon: Optional[Coupon]
    points_policy: PointsPolicy
    points_to_use: int
    payment_mode: PaymentMode
    shipping_fee: Decimal
    member_shipping_policy: Optional[ShippingPolicy]
    is_member: bool


@dataclass(frozen=True)
class SettlementSnapshot:
    original_price: Decimal
    after_member_discount: Decimal
    after_coupon: Decimal
    after_points: Decimal
    shipping_fee: Decimal
    final_total: Decimal
    points_used: int
    points_deduct_amount: Decimal


@dataclass(frozen=True)
class SettlementResult:
    total_payable: Decimal
    points_used: int
    points_deduct_amount: Decimal
    shipping_fee: Decimal
    snapshot: SettlementSnapshot


def _apply_member_discount(amount: Decimal, discount: Optional[Discount]) -> Decimal:
    if discount is None:
        return amount.quantize(Decimal("0.01"))
    return discount.apply(amount)


def _apply_coupon(amount: Decimal, coupon: Optional[Coupon]) -> Decimal:
    if coupon is None:
        return amount.quantize(Decimal("0.01"))
    return max(Decimal("0"), amount - coupon.amount).quantize(Decimal("0.01"))


def _calculate_points_deduction(
    amount: Decimal,
    policy: PointsPolicy,
    points_to_use: int,
    payment_mode: PaymentMode,
) -> tuple[int, Decimal]:
    if payment_mode == PaymentMode.CASH:
        return 0, Decimal("0.00")

    capped_points = min(points_to_use, policy.max_points)
    max_points_by_amount = int(
        (policy.max_deduct_amount / policy.points_to_currency_rate)
        .to_integral_value(rounding=ROUND_DOWN)
    )
    eligible_points = min(capped_points, max_points_by_amount)

    if payment_mode == PaymentMode.FULL_POINTS:
        max_points_by_balance = int(
            (amount / policy.points_to_currency_rate)
            .to_integral_value(rounding=ROUND_DOWN)
        )
        eligible_points = min(eligible_points, max_points_by_balance)

    deduct_amount = (policy.points_to_currency_rate * Decimal(eligible_points)).quantize(
        Decimal("0.01")
    )
    return eligible_points, min(amount, deduct_amount).quantize(Decimal("0.01"))


def _apply_shipping_policy(
    shipping_fee: Decimal,
    policy: Optional[ShippingPolicy],
    is_member: bool,
) -> Decimal:
    if not is_member or policy is None:
        return shipping_fee.quantize(Decimal("0.01"))
    if policy.free_shipping:
        return Decimal("0.00")
    if policy.discount is None:
        return shipping_fee.quantize(Decimal("0.01"))
    return policy.discount.apply(shipping_fee)


def settle_order(data: SettlementInput) -> SettlementResult:
    original_price = data.original_price.quantize(Decimal("0.01"))
    after_member_discount = _apply_member_discount(original_price, data.member_discount)
    after_coupon = _apply_coupon(after_member_discount, data.coupon)

    points_used, points_deduct_amount = _calculate_points_deduction(
        after_coupon,
        data.points_policy,
        data.points_to_use,
        data.payment_mode,
    )
    after_points = max(Decimal("0"), after_coupon - points_deduct_amount).quantize(
        Decimal("0.01")
    )

    shipping_fee = _apply_shipping_policy(
        data.shipping_fee,
        data.member_shipping_policy,
        data.is_member,
    )
    final_total = (after_points + shipping_fee).quantize(Decimal("0.01"))

    snapshot = SettlementSnapshot(
        original_price=original_price,
        after_member_discount=after_member_discount,
        after_coupon=after_coupon,
        after_points=after_points,
        shipping_fee=shipping_fee,
        final_total=final_total,
        points_used=points_used,
        points_deduct_amount=points_deduct_amount,
    )

    return SettlementResult(
        total_payable=final_total,
        points_used=points_used,
        points_deduct_amount=points_deduct_amount,
        shipping_fee=shipping_fee,
        snapshot=snapshot,
    )

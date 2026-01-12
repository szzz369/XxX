import unittest

from src.points_payments import PaymentMethod, PointsConfig, PointsPaymentService


class PointsPaymentServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PointsPaymentService(config=PointsConfig(ratio=0.1, max_deduction=50))
        self.service.register_wallet("customer", points=1000)

    def test_full_points_payment(self) -> None:
        order = self.service.create_order(
            customer_id="customer",
            order_id="order-1",
            total_amount=20,
            points_to_use=200,
            payment_method=None,
        )
        self.assertEqual(order.cash_amount, 0)
        self.service.handle_payment_success("customer", "order-1")
        wallet = self.service.wallets["customer"]
        self.assertEqual(wallet.available, 800)
        self.assertEqual(wallet.frozen, 0)

    def test_partial_points_payment(self) -> None:
        order = self.service.create_order(
            customer_id="customer",
            order_id="order-2",
            total_amount=60,
            points_to_use=200,
            payment_method=PaymentMethod.WECHAT,
        )
        self.assertEqual(order.cash_amount, 40)
        self.service.handle_payment_failure("customer", "order-2")
        wallet = self.service.wallets["customer"]
        self.assertEqual(wallet.available, 1000)
        self.assertEqual(wallet.frozen, 0)


if __name__ == "__main__":
    unittest.main()

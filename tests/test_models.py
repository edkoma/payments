import unittest
import json
from flask_api import status
from server import Payment, PaymentStatus, PaymentMethodType, PaymentMethod, app, db, DataValidationError
import logging


class TestModels(unittest.TestCase):

    def setUp(self):
        # Only log criticl errors
        app.debug = True
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.CRITICAL)
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_construct_a_payment(self):
        """Create a payment and assert that it exists and was properly initialized"""
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method=pm)
        self.assertTrue(payment != None)
        self.assertEqual(payment.user_id, 0)
        self.assertEqual(payment.order_id, 0)
        self.assertEqual(payment.status, PaymentStatus.UNPAID)
        self.assertEqual(payment.method, pm)

    def test_create_a_payment(self):
        """Create a payment and add it to the database"""
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method=pm)
        self.assertTrue(payment != None)
        payment.save()
        self.assertEqual(payment.id, 1)
        # This should be the only payment in the database, sqlite starts primary keys at 1
        p = Payment.find(1)
        self.assertEqual(p, payment)

    def test_find_payment(self):
        """Find a Payment by ID """
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        Payment(user_id=1, order_id=1, status=PaymentStatus.UNPAID,
            method=pm).save()
        Payment(user_id=2, order_id=2, status=PaymentStatus.PAID,
            method=pm).save()
        p = Payment.find(2)
        self.assertIsNot(p, None)
        self.assertEqual(p.id, 2)
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.order_id, 2)
        self.assertEqual(p.status, PaymentStatus.PAID)

    def test_find_payment_by_user(self):
        """Find a payment by its user ID"""
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        Payment(user_id=1, order_id=1, status=PaymentStatus.UNPAID,
            method=pm).save()
        Payment(user_id=2, order_id=2, status=PaymentStatus.PAID,
            method=pm).save()
        p = Payment.find_by_user(2).first()
        self.assertIsNot(p, None)
        self.assertEqual(p.id, 2)
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.order_id, 2)
        self.assertEqual(p.status, PaymentStatus.PAID)

    def test_find_payment_by_order(self):
        """Find a payment by its order ID"""
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        Payment(user_id=1, order_id=1, status=PaymentStatus.UNPAID,
            method=pm).save()
        Payment(user_id=2, order_id=2, status=PaymentStatus.PAID,
            method=pm).save()
        p = Payment.find_by_order(2).first()
        self.assertIsNot(p, None)
        self.assertEqual(p.id, 2)
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.order_id, 2)
        self.assertEqual(p.status, PaymentStatus.PAID)
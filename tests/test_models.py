import unittest
import json
from flask_api import status
from server import Payment, PaymentStatus, PaymentMethodType, PaymentMethod, app, db, DataValidationError
from vcap_services import get_database_uri
import logging
import os

class TestModels(unittest.TestCase):

    def setUp(self):
        # Only log criticl errors
        app.debug = True
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.CRITICAL)
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_construct_a_payment(self):
        """Create a payment and assert that it exists and was properly initialized"""
        # pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method_id=0)
        self.assertTrue(payment != None)
        self.assertEqual(payment.user_id, 0)
        self.assertEqual(payment.order_id, 0)
        self.assertEqual(payment.status, PaymentStatus.UNPAID)
        self.assertEqual(payment.method_id, 0)

    def test_create_a_payment(self):
        """Create a payment and add it to the database"""
        # pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method_id=0)
        self.assertTrue(payment != None)
        payment.save()
        self.assertEqual(payment.id, 1)
        # This should be the only payment in the database, sqlite starts primary keys at 1
        p = Payment.find(1)
        self.assertEqual(p, payment)

    def test_find_payment(self):
        """Find a Payment by ID """
        # pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        Payment(user_id=1, order_id=1, status=PaymentStatus.UNPAID,
            method_id=1).save()
        second_payment = Payment(user_id=2, order_id=2, status=PaymentStatus.PAID,
            method_id=2)
        second_payment.save()
        p = Payment.find(second_payment.id)
        self.assertIsNot(p, None)
        self.assertEqual(p.id, second_payment.id)
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.order_id, 2)
        self.assertEqual(p.status, PaymentStatus.PAID)

    def test_find_payment_by_user(self):
        """Find a payment by its user ID"""
        # pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        Payment(user_id=1, order_id=1, status=PaymentStatus.UNPAID,
            method_id=1).save()
        second_payment = Payment(user_id=2, order_id=2, status=PaymentStatus.PAID,
            method_id=2)
        second_payment.save()
        p = Payment.find_by_user(second_payment.user_id).first()
        self.assertIsNot(p, None)
        self.assertEqual(p.id, second_payment.id)
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.order_id, 2)
        self.assertEqual(p.status, PaymentStatus.PAID)

    def test_find_payment_by_order(self):
        """Find a payment by its order ID"""
        # pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        Payment(user_id=1, order_id=1, status=PaymentStatus.UNPAID,
            method_id=1).save()
        second_payment = Payment(user_id=2, order_id=2, status=PaymentStatus.PAID,
            method_id=1)
        second_payment.save()
        p = Payment.find_by_order(second_payment.order_id).first()
        self.assertIsNot(p, None)
        self.assertEqual(p.id, second_payment.id)
        self.assertEqual(p.user_id, 2)
        self.assertEqual(p.order_id, 2)
        self.assertEqual(p.status, PaymentStatus.PAID)

    def test_find_payment_method(self):
        """Find a Payment Method by ID """
        PaymentMethod(method_type=PaymentMethodType.CREDIT).save()
        second_paymentmethod = PaymentMethod(method_type=PaymentMethodType.DEBIT)
        second_paymentmethod.save()
        pm = PaymentMethod.find(second_paymentmethod.id)
        self.assertIsNot(pm, None)
        self.assertEqual(pm.id, second_paymentmethod.id)
        self.assertEqual(pm.method_type, PaymentMethodType.DEBIT)
        self.assertFalse(pm.is_default)

    def test_set_default_payment_method(self):
        """Set a payment method to be the default"""
        p1 = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        p2 = PaymentMethod(method_type=PaymentMethodType.DEBIT)
        self.assertFalse(p1.is_default)
        self.assertFalse(p2.is_default)
        p1.set_default()
        self.assertTrue(p1.is_default)
        self.assertFalse(p2.is_default)

    def test_recreate_table(self):
        """A test recreate table"""
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method_id=0)
        self.assertTrue(payment != None)
        payment.save()
        self.assertEqual(payment.id, 1)
        # This should be the only payment in the database, sqlite starts primary keys at 1
        p = Payment.find(1)
        self.assertEqual(p, payment)
        Payment.remove_all();
        p = Payment.find(1)
        self.assertNotEqual(p, payment)

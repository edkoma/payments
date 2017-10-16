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

    def test_update_payment(self):
        """Update an existing Payment"""
        pm = PaymentMethod(method_type=PaymentMethodType.DEBIT)
        new_payment = {'user_id': 0, "order_id": 0, 'status': PaymentStatus.UNPAID, 'method_id': method_id, 'method':}
        new_payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID, method=pm) 
        data =json.dumps(new_payment)
        resp = self.app.put('payments/1', data = data, content_type = 'application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['method_type'], 2)

    def test_update_payment_with_no_data(self):
        """ Update a Payment with no data passed """
        resp = self.app.put('/payments/2', data=None, content_type = 'application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_payment_not_found(self):
        """Update a Payment that does not exist"""
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        new_payment = Payment(user_id=0, order_id=0, status=PaymentStatus.PAID, method=pm)
        data = json.dumps(new_payment)
        resp = self.app.put('/pets/3', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

        
import unittest
import json
from server import Payment, PaymentStatus, PaymentMethodType, PaymentMethod, app, db
import logging

class TestPayments(unittest.TestCase):

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

    def test_create_a_payment(self):
        # Create a payment and assert that it exists
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method=pm)
        self.assertTrue(payment != None)
        self.assertEqual(payment.user_id, 0)
        self.assertEqual(payment.order_id, 0)
        self.assertEqual(payment.status, PaymentStatus.UNPAID)
        self.assertEqual(payment.method, pm)

    def test_add_a_payment(self):
        # Create a payment and add it to the database
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method=pm)
        self.assertTrue(payment != None)
        db.session.add(payment)
        db.session.commit()
        self.assertEqual(payment.id, 1)
        # This should be the only payment in the database, sqlite starts primary keys at 1
        p = Payment.query.get(1)
        self.assertEqual(p, payment)

     def test_get_payment(self):
        resp = self.app.get('/payments/2')
        #print 'resp_data: ' + resp.data
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual (data['user_id'], 'kitty')
        self.assertEqual (data['order_id'], 'kitty')
        self.assertEqual (data['status'], 'kitty')
        self.assertEqual (data['method_id'], 'kitty')
        self.assertEqual (data['method'], 'kitty')
        
import unittest
import json
from flask_api import status
from server import Payment, PaymentStatus, PaymentMethodType, PaymentMethod, app, db
import logging


class TestServer(unittest.TestCase):

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

    def test_get_home(self):
    	"""GET the home page"""
    	resp = self.app.get('/')
    	self.assertTrue('Payments Home Page' in resp.data)

    def test_post_a_payment(self):
        """Create a payment using a POST"""
        headers = {'Content-Type' : 'application/json'}
        js = {'user_id': 0, 'order_id': 0, 'status': PaymentStatus.UNPAID.value,
            'method_id': PaymentMethodType.CREDIT.value}
        resp = self.app.post('/payments', data=json.dumps(js), follow_redirects=True, headers=headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        get_resp = self.app.get('/payments/1')
        p = Payment()
        p.deserialize(json.loads(get_resp.data))
        self.assertEqual(p.id, 1)

    def test_post_an_invalid_payment(self):
        """POST a payment with invalid information"""
        headers = {'Content-Type' : 'application/json'}
        js = {'user_id': 0, 'order_id': 0, 'status': 'bad_data',
            'method_id': PaymentMethodType.CREDIT.value}
        resp = self.app.post('/payments', data=json.dumps(js), follow_redirects=True, headers=headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('body of request contained bad or no data' in resp.data)

    def test_post_a_payment_with_missing_information(self):
        """POST a payment with missing information"""
        headers = {'Content-Type' : 'application/json'}
        js = {'order_id': 0, 'status': PaymentStatus.UNPAID.value,
            'method_id': PaymentMethodType.CREDIT.value}
        resp = self.app.post('/payments', data=json.dumps(js), follow_redirects=True, headers=headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_a_payment(self):
        """Create a payment, then GET it"""
        pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
        payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID,
            method=pm)
        self.assertTrue(payment != None)
        payment.save()
        resp = self.app.get('/payments/1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        p = Payment() 
        p.deserialize(json.loads(resp.data))
        self.assertEqual(p.id, payment.id)
        self.assertEqual(p.user_id, payment.user_id)
        self.assertEqual(p.order_id, payment.order_id)
        self.assertEqual(p.status, payment.status)
        self.assertEqual(p.method_id, payment.method_id)

    def test_get_a_payment_404(self):
        """Try to GET a payment that doesn't exist"""
        resp = self.app.get('/payments/1')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

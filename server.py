

import os
import logging
from flask import Flask, Response, jsonify, request, json, make_response, url_for
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from werkzeug.exceptions import NotFound


######################################################################
# Init
######################################################################
app = Flask(__name__)
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# init SQLAlchemy db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/dev.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.create_all()

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass


######################################################################
# Routes
######################################################################

@app.route("/")
def home():
    return "Payments Home Page"

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(e):
    return make_response(jsonify(status=400, error='Bad Request', message=e.message), status.HTTP_400_BAD_REQUEST)


@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify(status=404, error='Not Found', message=e.description), status.HTTP_404_NOT_FOUND)


######################################################################
# Models
######################################################################

class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PROCESSING = "processing"
    PAID = "paid"
    

class PaymentMethodType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    PAYPAL = "paypal"

def create():
    pm = PaymentMethod(method_type=PaymentMethodType.CREDIT)
    payment = Payment(user_id=0, order_id=0, status=PaymentStatus.UNPAID, method=pm)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(PaymentStatus))
    method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), nullable=False)
    method = db.relationship('PaymentMethod', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return '<Payment %d>' % self.id


    def self_url(self):
        return url_for('get_payments', id=self.id, _external=True)

    def serialize(self):
        return {"id": self.id, "user_id": self.user_id, "order_id": self.order_id,
                "status": self.status, "method_id": self.method_id, "method": self.method}

    def serialize_methods(self):
        return{"method_id": self.method_id, "method": self.method}
    
    def deserialize(self, data):
        try:
            self.id = data['id']
            self.user_id = data['user_id']
            self.order_id = data['order_id']
            self.status = data['status']
            self.method_id = data['method_id']
            self.method = data['method']
        except KeyError as e:
            raise DataValidationError('Invalid payment: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid payment: body of request contained bad or no data')
        return self


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method_type = db.Column(db.Enum(PaymentMethodType))

    def __repr__(self):
        return '<PaymentMethod %d, type %r>' % (self.id, self.method_type)

######################################################################
# LIST ALL PAYMENTS
######################################################################
@app.route('/payments', methods=['GET'])
def list_payments():
    payments = []

    results = [payments.serialize() for payments in payments]
    print results
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# LIST ALL PAYMENT METHODS
######################################################################
@app.route('/payments/methods', methods=['GET'])
def list_payment_methods():
    payment_methods = []
    method = Payment.query.get('method')
    if method:
        payment_methods = Payment.query.filter(Payment.method == method)

    results = [p.serialize_methods() for p in payment_methods]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PAYMENT
######################################################################
@app.route('/payments/<int:id>', methods=['GET'])
def get_payments(id):
    payment = Payment.query.get(id)
    if not payment:
        raise NotFound("Payment with id: '{}' was not found in the database.".format(id))
    return make_response(jsonify(payment.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PAYMENT
######################################################################
@app.route('/payments', methods=['POST'])
def create_payment():
    payment = Payment()
    payment.deserialize(request.get_json())
    db.session.add(payment)
    db.session.commit()
    message = payment.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': payment.self_url() })

######################################################################
# Main
######################################################################

if __name__ == "__main__":
    db.create_all()
    create()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
import os
import logging
from flask import Flask, Response, jsonify, request, json, make_response, url_for
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from enum import Enum


######################################################################
# Init
######################################################################
app = Flask(__name__)
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# init SQLAlchemy db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passw0rd@localhost/payments'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.create_all()

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass


# This needs to be after db, classes, etc are initialized to avoid circular imports
from models import *

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
# LIST ALL PAYMENTS
######################################################################
@app.route('/payments', methods=['GET'])
def list_payments():
    user_id = request.args.get('user')
    order_id = request.args.get('order')
    if user_id:
        payments = Payment.find_by_user(user_id)
    elif order_id:
        payments = Payment.find_by_order(order_id)
    else:
        payments = Payment.all()
    results = [payment.serialize() for payment in payments]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PAYMENT
######################################################################
@app.route('/payments/<int:id>', methods=['GET'])
def get_payment(id):
    payment = Payment.find_or_404(id)
    return make_response(jsonify(payment.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING PAYMENT
######################################################################
@app.route('/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    payment = Payment.find_or_404(id)
    payment.deserialize(request.get_json())
    payment.id = id
    payment.save()
    return make_response(jsonify(payment.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PAYMENT
######################################################################
@app.route('/payments', methods=['POST'])
def create_payment():
    payment = Payment()
    payment.deserialize(request.get_json())
    payment.save()
    message = payment.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': payment.self_url() })

######################################################################
# DELETE A PAYMENT
######################################################################
@app.route('/payments/<int:id>', methods=['DELETE'])
def delete_payment(id):
    payment = Payment.find(id)
    if payment:
        payment.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# LIST ALL PAYMENT METHODS
######################################################################
@app.route('/payments/methods', methods=['GET'])
def list_payment_methods():
    payment_methods = PaymentMethod.all()
    results = [ pm.serialize() for pm in payment_methods]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PAYMENT METHOD
######################################################################
@app.route('/payments/methods/<int:id>', methods=['GET'])
def get_payment_method(id):
    pm = PaymentMethod.find_or_404(id)
    return make_response(jsonify(pm.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING PAYMENT METHOD
######################################################################
@app.route('/payments/methods/<int:id>', methods=['PUT'])
def update_payment_method(id):
    print(request.get_json())
    pm = PaymentMethod.find_or_404(id)
    pm.deserialize(request.get_json())
    pm.id = id
    pm.save()
    return make_response(jsonify(pm.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PAYMENT METHOD
######################################################################
@app.route('/payments/methods', methods=['POST'])
def create_payment_method():
    pm = PaymentMethod()
    pm.deserialize(request.get_json())
    pm.save()
    message = pm.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': pm.self_url() })

######################################################################
# DELETE A PAYMENT METHOD
######################################################################
@app.route('/payments/methods/<int:id>', methods=['DELETE'])
def delete_payment_method(id):
    pm = PaymentMethod.find(id)
    if pm:
        pm.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# SET PAYMENT METHOD AS DEFAULT
######################################################################
@app.route('/payments/methods/<int:id>/set-default', methods=['PUT'])
def set_payment_method_default(id):
    pm = PaymentMethod.find_or_404(id)
    pm.set_default()
    return make_response(jsonify(pm.serialize(), status.HTTP_200_OK))

######################################################################
# Main
######################################################################

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)

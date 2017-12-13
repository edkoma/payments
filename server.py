import os
import logging
from flask import Flask, Response, jsonify, request, json, make_response, url_for
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from enum import Enum
from vcap_services import get_database_uri


######################################################################
# Init
######################################################################
app = Flask(__name__)
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.create_all()

######################################################################
# Configure Swagger before initilaizing it
######################################################################
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "Swagger Payments Service",
            "description": "This is a Payments REST service.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

######################################################################
# Configure Swagger before initilaizing it
######################################################################
Swagger(app)

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
    return app.send_static_file('index.html')

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
    """
    Retrieves a list of payments.
    This endpoint will return all Payments unless a query parameter is specified.
    ---
    tags:
      - Payments
    description: The Payments endpoint allows you to query Payments
    parameters:
      - name: user_id
        in: query
        description: the user id of the payment in the system
        required: false
        type: string
      - name: order_id
        in: query
        description: The order id of the payment in the system
        required: false
        type: string
      - name: status
        in: query
        description: Describes if the payment is UNPAID, PROCESSING, or PAID
        required: false
        type: string
      - name: method_id
        in: query
        description: The method id of the payment in the system
        required: false
        type: string
    responses:
      200:
        description: A list of payments
        schema:
          type: array
          items:
            schema:
              id: Payment
              properties:
                id:
                  type: integer
                  description: unique id assigned internally by Service
                user_id:
                  type: integer
                  description: The user id of the payment in the system
                order_id:
                  type: integer
                  description: The order id of the payment in the system
                status:
                  type: string
                  description: Describes if the payment is UNPAID, PROCESSING, or PAID
                method_id:
                  type: integer
                  description: The method id of the payment in the system
    """
    user_id = request.args.get('user_id')
    order_id = request.args.get('order_id')
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
    """
    Retrieves a single Payment
    This endpoint will return a Payment based on it's id
    ---
    tags:
        - Payments
    produces:
        - application/json
    parameters:
      - name: id
        in: path
        description: ID of payment to retrive
        type: integer
        required: true
    responses:
        200:
            description: Payment returned with that id
            schema:
                id: Payment
                properties:
                    id:
                        type: integer
                        description: Unique id assigned internally by service
                    user_id:
                        type: integer
                        description: The user id of the payment in the system
                    order_id:
                        type: integer
                        description: The order id of the payment in the system
                    status:
                        type: string
                        description: Describes if the payment is UNPAID, PROCESSING, or PAID
                    method_id:
                        type: integer
                        description: The method id of the payment in the system
        404:
            description: Payment not found
    """
    payment = Payment.find_or_404(id)
    return make_response(jsonify(payment.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING PAYMENT
######################################################################
@app.route('/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    """
    Update a Payment
    This endpoint will update a payment based on the body that is posted
    ---
    tags:
        - Payments
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
        - name: id
          in: path
          description: ID of payment to retrieve
          type: integer
          required: true
        - name: user_id
          in: path
          description: user id of payment in the system
          type: integer
          required: true
        - name: order_id
          in: path
          description: order id of payment in the system
          type: integer
          required: true
        - name: status
          in: path
          description: ID of payment to retrieve
          type: integer
          required: true
        - name: method_id
          in: path
          description: ID of payment to retrieve
          type: integer
          required: true


    responses:
        200:
            description: Payment updated
            schema:
                id: Payment
                properties:
                    id:
                        type: integer
                        description: Unique id assigned internally by service
                    user_id:
                        type: integer
                        description: The user id of the payment in the system
                    order_id:
                        type: integer
                        description: The order id of the payment in the system
                    status:
                        type: string
                        description: Describes if the payment is UNPAID, PROCESSING, or PAID
                    method_id:
                        type: integer
                        description: The method id of the payment in the system
        400:
            description: Bad Request
    """

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
    """
    Create a payment
    This endpoint will create a payment based on the data in the body that is posted.
    ---
    tags:
        - Payments
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
        - in: body
          user_id: body
          required: true
        - in: body
          order_id: body
          required: true
        - in: body
          status: body
          required: true
        - in: body
          method_id: body
          required: true
          schema:
            id: data
            required:
                - user_id
                - order_id
                - status
                - method_id
            responses:
                201:
                    description: Payment created
                    schema:
                        id: Payment
                        properties:
                            id:
                                type: integer
                                description: unique id assigned internally be service
                            user_id:
                                type: integer
                                description: The user id of the payment in the system
                            order_id:
                                type: integer
                                description: The order id of the payment in the system
                            status:
                                type: string
                                description: Describes if the payment is UNPAID, PROCESSING, or PAID
                            method_id:
                                type: integer
                                description: The method id of the payment in the system
                400:
                    description: Bad Request
        """

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
    """
    Delete a Payment
    This endpoint will delete a Payment based on the id specified in the path.
    ---
    tags:
        - Payments
    description: Deletes a Payment from the database
    parameters:
      - name: id
        in: path
        description: ID of payment to delete
        type: integer
        required: true
    responses:
        204:
            description: Payment deleted
    """

    payment = Payment.find(id)
    if payment:
        payment.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# LIST ALL PAYMENT METHODS
######################################################################
@app.route('/payments/methods', methods=['GET'])
def list_payment_methods():
    """
    Retrieve a list of payment methods.
    This endpoint will return all payment methods unless a query parameter is specified.
    ---
    tags:
      - Payment Methods
    description: The methods endpoint allows you to query methods
    responses:
        200:
            description: An array of Payment methods
            schema:
                type: array
                items:
                    schema:
                        id: PaymentMethod
                        properties:
                            id:
                                type: integer
                                description: unique id assigned internally be service
                            method_type:
                                type: string
                                description: The type of payment method
                                enum:
                                - CREDIT
                                - DEBIT
                                - PAYPAL
                            is_default:
                                type: boolean
                                description: Signals that this is the default payment method
    """

    payment_methods = PaymentMethod.all()
    results = [ pm.serialize() for pm in payment_methods]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PAYMENT METHOD
######################################################################
@app.route('/payments/methods/<int:id>', methods=['GET'])
def get_payment_method(id):
    """
    Retrieve a single payment method
    This endpoint will return a Payment method based on its id
    ---
    tags:
        - Payment Methods
    produces:
        - application/json
    parameters:
        - name: id
          in: path
          description: ID of payment method to retrieve
          type: integer
          required: true
    responses:
        200:
            description: Payment method returned
            schema:
                id: PaymentMethod
                properties:
                    id:
                        type: integer
                        description: unique id assigned internally be service
                    method_type:
                        type: string
                        description: The type of payment method
                        enum:
                        - CREDIT
                        - DEBIT
                        - PAYPAL
                    is_default:
                        type: boolean
                        description: Signals that this is the default payment method
        404:
            description: Payment method not found
    """

    pm = PaymentMethod.find_or_404(id)
    return make_response(jsonify(pm.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING PAYMENT METHOD
######################################################################
@app.route('/payments/methods/<int:id>', methods=['PUT'])
def update_payment_method(id):
    """
    Update a payment method
    This endpoint will update a payment method based on the id that is posted.
    ---
    tags:
        - Payment Methods
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
        - name: id
          in: path
          description: id of payment method to retrieve
          type: integer
          required: true
        - name: method_type
          in: path
          description: type of payment method
          type: string
          required: true
        - name: is_default
          in: path
          description: specifies whether payment method is default
          type: string
          required: true

    responses:
        200:
            description: Payment method updated
            schema:
                id: PaymentMethod
                properties:
                    id:
                        type: integer
                        description: unique id assigned internally by service
                    method_type:
                        type: string
                        description: The type of payment method
                        enum:
                        - CREDIT
                        - DEBIT
                        - PAYPAL
                    is_default:
                        type: boolean
                        description: Signals that this is the default payment method
        400:
            description: Bad Request
    """
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
    """
    Make a new payment method.
    This endpoint will make a payment method.
    ---
    tags:
        - Payment Methods
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
        - in: body
          method_type: body
          required: true
        - in: body
          is_default: body
          required: true
          schema:
            id: data
            required:
                 - method_type
                 - is_default
            properties:
                id:
                    type: integer
                    description: unique id assigned internally by service
                method_type:
                    type: string
                    description: The type of payment method
                    enum:
                        - CREDIT
                        - DEBIT
                        - PAYPAL
                is_default:
                    type: boolean
                    description: Signals that this is the default payment method
    responses:
        201:
            description: Payment method created
            schema:
                id: PaymentMethod
                properties:
                    id:
                        type: integer
                        description: unique id assigned internally be service
                    method_type:
                        type: string
                        description: The type of payment method
                        enum:
                        - CREDIT
                        - DEBIT
                        - PAYPAL
                    is_default:
                        type: boolean
                        description: Signals that this is the default payment method

    """
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
    """
    Delete a payment method
    This endpoint will delete a payment method based on the id specified in its path.
    ---
    tags:
        - Payment Methods
    description: Deletes a payment method from the database
    parameters:
      - name: id
        in: path
        description: method id of payment to delete
        type: integer
        required: true
    responses:
        204:
            description: Payment Method deleted
    """

    pm = PaymentMethod.find(id)
    if pm:
        pm.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# SET PAYMENT METHOD AS DEFAULT
######################################################################
@app.route('/payments/methods/<int:id>/set-default', methods=['PUT'])
def set_payment_method_default(id):
    """
    Set a default payment method.
    This endpoint will set a default payment method.
    ---
    tags:
        - Payment Methods
    description: Set a payment method as the default
    parameters:
      - name: id
        in: path
        description: method id of payment to make default
        type: integer
        required: true
    responses:
        200:
            description: Payment method set to default
            schema:
                id: PaymentMethod
                properties:
                    id:
                        type: integer
                        description: unique id assigned internally be service
                    method_type:
                        type: string
                        description: The type of payment method
                        enum:
                        - CREDIT
                        - DEBIT
                        - PAYPAL
                    is_default:
                        type: boolean
                        description: Signals that this is the default payment method

    """
    pm = PaymentMethod.find_or_404(id)
    pm.set_default()
    return make_response(jsonify(pm.serialize(), status.HTTP_200_OK))

######################################################################
# Main
######################################################################

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)

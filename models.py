from server import db, DataValidationError
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask import url_for


class PaymentStatus(Enum):
    UNPAID = 1
    PROCESSING = 2
    PAID = 3

class PaymentMethodType(Enum):
    __order__ ='CREDIT DEBIT PAYPAL'
    CREDIT = 1
    DEBIT = 2
    PAYPAL = 3

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(PaymentStatus))
    method_id = db.Column(db.Integer, nullable=False)
    # method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), nullable=False)
    # method = db.relationship('PaymentMethod', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return '<Payment %d>' % self.id

    def save(self):
        """ Saves an existing Payment in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Delete a Payment from the database"""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def all():
        """ Return all of the Payments in the database """
        return Payment.query.all()

    @staticmethod
    def find(payment_id):
        """ Find a Payment by its id """
        return Payment.query.get(payment_id)

    @staticmethod
    def find_or_404(payment_id):
        """ Find a Payment by its id """
        return Payment.query.get_or_404(payment_id)

    @staticmethod
    def find_by_user(user_id):
        """ Find a Payment/s by its user id"""
        return Payment.query.filter(Payment.user_id == user_id)

    @staticmethod
    def find_by_order(order_id):
        """ Find a Payment/s by its order id"""
        return Payment.query.filter(Payment.order_id == order_id)

    def self_url(self):
        return url_for('get_payment', id=self.id, _external=True)

    def serialize(self):
        return {"id": self.id, "user_id": self.user_id, "order_id": self.order_id,
                "status": self.status.value, "method_id": self.method_id}

    def deserialize(self, data):
        try:
            # Won't have an id yet if this is when it's being created for the first time
            if 'id' in data:
                self.id = data['id']
            self.user_id = data['user_id']
            self.order_id = data['order_id']
            self.status = PaymentStatus(data['status'])
            self.method_id = data['method_id']
        except KeyError as e:
            raise DataValidationError('Invalid payment: missing ' + e.args[0])
        except (TypeError, ValueError) as e:
            raise DataValidationError('Invalid payment: body of request contained bad or no data')
        return self


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method_type = db.Column(db.Enum(PaymentMethodType))
    is_default = db.Column(db.Boolean, default=False)

    def save(self):
        """ Saves an existing Payment Method in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def find(id):
        """ Find a Payment Method by its id """
        return PaymentMethod.query.get(id)

    def delete(self):
        """ Delete a Payment Methodfrom the database"""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def all():
        """ Return all of the Payment Methods in the database """
        return PaymentMethod.query.all()

    @staticmethod
    def find_or_404(payment_id):
        """ Find a Payment by its id """
        return PaymentMethod.query.get_or_404(payment_id)

    def self_url(self):
        return url_for('get_payment_method', id=self.id, _external=True)

    def serialize(self):
        return {"id": self.id, "method_type": self.method_type.value, "is_default": self.is_default}

    def deserialize(self, data):
        try:
            # Won't have an id yet if this is when it's being created for the first time
            if 'id' in data:
                self.id = data['id']
            self.method_type = PaymentMethodType(data['method_type'])
            if 'is_default' in data:
                self.is_default = data['is_default']
            else:
                self.is_default = False
        except KeyError as e:
            raise DataValidationError('Invalid payment method: missing ' + e.args[0])
        except (TypeError, ValueError) as e:
            raise DataValidationError('Invalid payment method: body of request contained bad or no data')
        return self

    def set_default(self):
        """Sets a payment method to be the default"""
        self.is_default = True
        self.save()


    def __repr__(self):
        return '<PaymentMethod %d, type %r>' % (self.id, self.method_type)

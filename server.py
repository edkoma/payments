import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from models import db

######################################################################
# Init
######################################################################
app = Flask(__name__)
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# init SQLAlchemy db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

######################################################################
# Routes
######################################################################

@app.route("/")
def home():
    return "Payments Home Page"

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

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(PaymentStatus))
    method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), nullable=False)
    method = db.relationship('PaymentMethod', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return '<Payment %d>' % self.id



class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method_type = db.Column(db.Enum(PaymentMethodType))

    def __repr__(self):
        return '<PaymentMethod %d, type %r>' % (self.id, self.method_type)

######################################################################
# Main
######################################################################

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
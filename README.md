# payments
[![Build Status](https://travis-ci.org/nyu-devops-payments-2017/payments.svg?branch=master)](https://travis-ci.org/nyu-devops-payments-2017/payments)
DevOps Fall 2017 Payment Service

Simulates a payment system for an e-commerce site. Basic CRUD actions are available to create, read, update, and delete payments and payment methods.

The app is deployed on [Bluemix](nyu-payment-service-f17.mybluemix.net), and can also be tested locally.
To set up your own local copy, `git clone` the repository, then run `vagrant up` in the newly created directory. Run `vagrant ssh` to enter the virtual machine, then `cd /vagrant` and `python server.py` to start the Flask server, which will appear on localhost.
You can also run `nosetests` to make sure everything is working.

`GET`, `PUT`, `POST`, and `DELETE` calls can be made to the `/payments` and `/payments/methods` endpoints, to perform the expected actions. More information on the API can be found in the Swagger documentation. Note that to create a Payment, you will likely need to create a PaymentMethod first.
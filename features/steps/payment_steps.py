"""
Payment Steps
Steps file for payments.feature
"""
from os import getenv
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import server

WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')

@given(u'the following payments')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(BASE_URL + '/payments/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = BASE_URL + '/payments'
    for row in context.table:
        data = {
         	"user_id": int(row['user_id']),
            "order_id": int(row['order_id']),
            "status": int(row['status']),
            "method_id": int(row['method_id'])
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


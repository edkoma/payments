"""
Payment Steps
Steps file for payments.feature
"""
"""Create, Read, Update, Delete, Query, Action"""
from os import getenv
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.remote.webelement import WebElement
import server
from models import PaymentStatus
from models import PaymentMethodType
import time


WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')

@given(u'the following payments')
def step_impl(context):
    """ Delete all Payments and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(BASE_URL + '/payments/reset', headers=headers)
    #expect(context.resp.status_code).to_equal(204)
    create_url = BASE_URL + '/payments'
    temp_id = 0
    for row in context.table:
        data = {
         	"user_id": int(row['user_id']),
            "order_id": int(row['order_id']),
            "status": int(row['status']),
            "method_id": int(row['method_id'])
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        temp_resp = json.loads(context.resp.text)
        temp_id = temp_resp['id']
        expect(context.resp.status_code).to_equal(201)
    #Since sqlalchemy autoincrements the id, I am getting the  last ID and passing it the context for testing
    context.temp_id = temp_id

@when(u'I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(BASE_URL)
    #context.resp = context.app.get('/')

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then(u'I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)

@when(u'I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()
    #time.sleep(45)

@then(u'I should see user_id "{name}" in the results')
def step_impl(context, name):
    #element = context.driver.find_element_by_id('search_results')
    #expect(element.text).to_contain(name)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    if element_name == 'id':
        text_string = str(context.temp_id)
    #print(text_string)
    element_id = 'payment_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when(u'I set the status option to "{text_string}"')
def step_impl(context, text_string):
    element_id = 'payment_status'
    element = context.driver.find_element_by_id(element_id)
    for option in element.find_elements_by_tag_name('option'):
        if option.text == PaymentStatus(int(text_string)).name:
            option.click() # select() in earlier versions of webdriver
            break

@when(u'I set the method_id option to "{text_string}"')
def step_impl(context, text_string):
    element_id = 'payment_method_id'
    element = context.driver.find_element_by_id(element_id)
    for option in element.find_elements_by_tag_name('option'):
        if option.text == PaymentMethodType(int(text_string)).name:
            option.click() # select() in earlier versions of webdriver
            break

@then(u'I should see the message "{message}"')
def step_impl(context, message):
    #element = context.driver.find_element_by_id('flash_message')
    #expect(element.text).to_contain(message)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'payment_' + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context,text_string,element_name):
    element_id = 'payment_' + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    #expect(element.get_attribute('value')).to_equal(text_string)
    expect(found).to_be(True)

@then(u'I should not see user_id "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    #print(element.text)
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

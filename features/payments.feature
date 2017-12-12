Feature: The pet store service back-end
    As a Payments Owner
    I need a RESTful payments service
    So that I can keep track of all my payments

Background:
    Given the following payments:
      | id | user_id | order_id | status    | method_id
      |  0 |    1    |   2      | UNPAID    |   1
      |  1 |    2    |   3      | PAID      |   3
      |  2 |    3    |   4      | PROCESSING|   2

Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Payments Home Page" 
        And I should not see "404 Not Found"

Scenario: List all payments
        When I visit "payments"
        Then I should see id "0" in the results
        And I should see id "1" in the results
        And I should see id "2" in the results

Scenario: Create a payment
        When I visit the "Home Page"
        And I add a new payment
        And I set the user_id to 4
        And I set the order_id to 1
        And I set the status to PAID
        And I set the method_id to 3
        And I click the "Create" button
        Then I should see all the payments, including the latest payment

Scenario: Update an existing payment
        When I visit the "Home Page"
        And I specify the id to "1"
        And I press the "Retrieve" button
        Then I should see the user id to "2"
        When I change user id to "3"
        And I press the "Update" button
        Then I should see the message "Success"
        When I specify the id as "1"
        And I press the "Retrieve" button
        Then I should see user id to "3"

Scenario: Delete a payment
        When I delete a payment with id "0"
        Then I should get a response code of "204"
        When I visit "payments"
        Then I should see user id of "2"
        And I should see user id of "3"
        And I should not see user id of "1"
        Then there should be 2 payments

Scenario: Read a payment
        When I read a payment with a specific id
        Then I should get a response code of "200"
        And I should see the entire record of that id

Scenario: Find all payments with user id
        When I specify a payment with a user id
        Then I should return a payment with only that user id

Scenario: Setting a default payment method
        When we set an id as being default
        Then we get a response code of "200"
        And we verify that the user id is being set as default.

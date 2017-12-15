Feature: The pet store service back-end
    As a Payments Owner
    I need a RESTful payments service
    So that I can keep track of all my payments

Background:
    Given the following payments:
      | id | user_id | order_id | status    | method_id |
      |  0 |    4    |   7      | 1         |   1       |
      |  1 |    5    |   8      | 3         |   3       |
      |  2 |    6    |   9      | 2         |   2       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "NYU DevOps Fall 2017 Payments" in the title
    And I should not see "404 Not Found"

Scenario: List all payments
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see user_id "4" in the results
    And I should see user_id "5" in the results
    And I should see user_id "6" in the results

Scenario: Create a Payment
    When I visit the "Home Page"
    And I set the "user_id" to "11"
    And I set the "order_id" to "10"
    And I set the status option to "1"
    And I set the method_id option to "2"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: Update an existing payment
    When I visit the "Home Page"
    And I set the "id" to "2"
    And I press the "retrieve" button
    Then I should see "6" in the "user_id" field
    When I change "user_id" to "8"
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "id" to "2"
    And I press the "Retrieve" button
    Then I should see "8" in the "user_id" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see user_id "8" in the results


  Scenario: Query an existing payment
    When I visit the "Home Page"
    And I set the "id" to "2"
    And I press the "retrieve" button
    Then I should see "6" in the "user_id" field
    Then I should see "9" in the "order_id" field
    Then I should see "2" in the "status" field

  Scenario: Delete an existing payment
    When I visit the "Home Page"
    And I set the "id" to "2"
    And I press the "delete" button
    And I press the "search" button
    Then I should see the message "Success"
    And I should see user_id "4" in the results
    And I should see user_id "5" in the results

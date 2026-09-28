# Amazon Connect Customer Routing Flow

## Purpose

This contact flow is designed for an inbound customer-support contact center.

The flow collects a customer ID, invokes the `customer-lookup` AWS Lambda function, retrieves customer information from DynamoDB, and routes the caller according to their support tier.

## Flow

1. Customer calls the Amazon Connect contact center.
2. Play a welcome message.
3. Ask the customer to enter their customer ID.
4. Store the customer ID as a contact attribute.
5. Invoke the `customer-lookup` Lambda function.
6. Lambda queries the `Customers` DynamoDB table.
7. Check the Lambda response:
   - `SUCCESS` + `supportTier = Priority` → Priority Support queue
   - `SUCCESS` + `supportTier = Normal` → General Support queue
   - `NOT_FOUND` → Ask the customer to try again or transfer to General Support
   - `ERROR` → Transfer to General Support
8. Agent receives the routed customer contact.

## Logical Flow

Customer
  |
  v
Welcome Message
  |
  v
Get Customer ID
  |
  v
Invoke customer-lookup Lambda
  |
  v
Customers DynamoDB Table
  |
  v
Check supportTier
  |
  +-------------------+
  |                   |
  v                   v
Priority            Normal
  |                   |
  v                   v
Priority Queue     General Queue

## Lambda Response

Example successful response:

```json
{
  "status": "SUCCESS",
  "customerId": "CUST1001",
  "name": "Rahul Sharma",
  "accountNumber": "ACC1001",
  "customerType": "Premium",
  "supportTier": "Priority"
}

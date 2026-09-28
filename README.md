# Cloud Contact Center Solution

A serverless cloud contact-center solution designed using AWS services.

This project demonstrates customer lookup, serverless processing, DynamoDB data storage, IAM least-privilege access, CloudWatch monitoring, and an Amazon Connect-based contact-center architecture.

> **Note:** The Amazon Connect architecture and contact flow are designed and documented, but an Amazon Connect instance could not be provisioned because of an AWS account-level restriction. The repository does not claim that Amazon Connect was successfully deployed.

---

## Architecture

The planned architecture is:

```text
                         +----------------------+
                         |       Customer       |
                         +----------+-----------+
                                    |
                                    | Inbound Call
                                    v
                         +----------------------+
                         |   Amazon Connect     |
                         |   Contact Center     |
                         +----------+-----------+
                                    |
                                    | Customer ID
                                    v
                         +----------------------+
                         |     AWS Lambda       |
                         |   customer-lookup    |
                         +----------+-----------+
                                    |
                                    | GetItem
                                    v
                         +----------------------+
                         |   Amazon DynamoDB    |
                         |      Customers       |
                         +----------+-----------+
                                    |
                                    | Customer Record
                                    v
                         +----------------------+
                         |   Routing Decision   |
                         +----------+-----------+
                                    |
                          +---------+---------+
                          |                   |
                          v                   v
                  +---------------+   +---------------+
                  | Priority Queue|   | General Queue |
                  +---------------+   +---------------+
```

### Planned Routing Logic

The routing decision uses the customer's `supportTier` returned by AWS Lambda.

```text
Customer Call
     |
     v
Amazon Connect
     |
     v
Collect Customer ID
     |
     v
Invoke AWS Lambda
     |
     v
Query DynamoDB
     |
     v
Check supportTier
     |
     +-------------------+
     |                   |
     v                   v
 Priority              Normal
     |                   |
     v                   v
Priority Queue       General Queue
```

### Routing Rules

| Customer Support Tier | Destination             |
| --------------------- | ----------------------- |
| Priority              | Priority Support        |
| Normal                | General Support         |
| Customer Not Found    | General Support / Retry |
| Error                 | General Support         |

The routing logic is documented in:

```text
contact-flows/customer-routing-flow.md
```

---

## AWS Services

| AWS Service       | Purpose                                                 |
| ----------------- | ------------------------------------------------------- |
| Amazon Connect    | Contact-center and call-routing architecture            |
| AWS Lambda        | Serverless customer lookup                              |
| Amazon DynamoDB   | Customer information storage                            |
| AWS IAM           | Least-privilege permissions                             |
| Amazon CloudWatch | Lambda execution logs and monitoring                    |
| Amazon S3         | Amazon Connect data storage when Connect is provisioned |

---

## Project Structure

```text
Cloud-Contact-Center-Solution/
│
├── contact-flows/
│   └── customer-routing-flow.md
│
├── dynamodb/
│   └── sample-customer-data.json
│
├── iam/
│   └── lambda-dynamodb-policy.json
│
├── lambda/
│   └── customer_lookup.py
│
├── screenshots/
│
└── README.md
```

---

# AWS Lambda

## Function

```text
customer-lookup
```

## Purpose

The AWS Lambda function retrieves customer information from DynamoDB based on the provided customer ID.

### Processing Flow

```text
Customer ID
    |
    v
AWS Lambda
    |
    v
Validate Customer ID
    |
    v
DynamoDB GetItem
    |
    v
Customer Record
    |
    v
Return Customer Information
```

## Source Code

```text
lambda/customer_lookup.py
```

## Runtime

```text
Python 3.14
```

## Architecture

```text
x86_64
```

## Example Input

```json
{
  "customerId": "CUST1001"
}
```

## Example Output

```json
{
  "status": "SUCCESS",
  "customerId": "CUST1001",
  "name": "Rahul Sharma",
  "accountNumber": "ACC1001",
  "customerType": "Premium",
  "supportTier": "Priority"
}
```

---

# Amazon DynamoDB

## Table

```text
Customers
```

## Region

```text
ap-south-1
```

## Partition Key

```text
customerId
```

## Key Type

```text
String
```

## Capacity Mode

```text
On-demand
```

## Purpose

Amazon DynamoDB stores customer information used by the customer lookup Lambda function.

### Customer Attributes

```text
customerId
name
accountNumber
customerType
supportTier
```

### Data Flow

```text
AWS Lambda
    |
    | GetItem
    v
Customers Table
    |
    v
Customer Record
```

Sample customer data is stored in:

```text
dynamodb/sample-customer-data.json
```

---

# AWS IAM

AWS IAM is used to provide the Lambda function with controlled access to the DynamoDB table.

## Least-Privilege Permission

The Lambda function requires only:

```text
dynamodb:GetItem
```

The Lambda function does not require permission to modify or delete customer records.

## IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadCustomersTable",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/Customers"
    }
  ]
}
```

`REGION` and `ACCOUNT_ID` are used as placeholders to avoid exposing account-specific information.

Policy file:

```text
iam/lambda-dynamodb-policy.json
```

---

# Customer Workflow

The planned customer workflow is:

1. Customer calls the support center.
2. Amazon Connect receives the inbound call.
3. A welcome message is played.
4. Customer provides the customer ID.
5. The customer ID is stored as a contact attribute.
6. Amazon Connect invokes the Lambda function.
7. Lambda validates the customer ID.
8. Lambda queries DynamoDB.
9. DynamoDB returns the customer record.
10. Lambda returns the customer information.
11. The contact flow checks the support tier.
12. The customer is routed to the appropriate queue.

### Workflow Diagram

```text
Customer
   |
   v
Amazon Connect
   |
   v
Welcome Message
   |
   v
Customer ID
   |
   v
AWS Lambda
   |
   v
Amazon DynamoDB
   |
   v
Customer Information
   |
   v
Support Tier
   |
   +----------------------+
   |                      |
   v                      v
Priority                Normal
   |                      |
   v                      v
Priority Queue       General Queue
```

---

# Lambda and DynamoDB Integration

AWS Lambda communicates with Amazon DynamoDB using the AWS SDK for Python (`boto3`).

### Integration

```text
Customer ID
     |
     v
AWS Lambda
     |
     | GetItem
     v
Amazon DynamoDB
     |
     v
Customers Table
     |
     v
Customer Record
     |
     v
Lambda Response
```

### DynamoDB Lookup

The Lambda function performs a DynamoDB `GetItem` operation:

```python
response = table.get_item(
    Key={"customerId": customer_id}
)
```

### Successful Lookup

```json
{
  "status": "SUCCESS",
  "customerId": "CUST1001",
  "name": "Rahul Sharma",
  "accountNumber": "ACC1001",
  "customerType": "Premium",
  "supportTier": "Priority"
}
```

---

# Testing

The Lambda function was tested using the AWS Lambda test console.

## Test Event

```json
{
  "customerId": "CUST1001"
}
```

## Expected Result

```json
{
  "status": "SUCCESS",
  "customerId": "CUST1001",
  "name": "Rahul Sharma",
  "accountNumber": "ACC1001",
  "customerType": "Premium",
  "supportTier": "Priority"
}
```

## Test Verification

The successful test confirmed the following flow:

```text
AWS Lambda
    |
    v
DynamoDB GetItem
    |
    v
Customers Table
    |
    v
Customer Record
    |
    v
Successful Lambda Response
```

### Error Test

An unknown customer ID returns:

```json
{
  "status": "NOT_FOUND",
  "customerId": "CUST9999"
}
```

A missing customer ID returns:

```json
{
  "status": "ERROR",
  "message": "customerId is required"
}
```

---

# Sample Customer Data

The project uses fictional customer data for development and testing.

### Customer 1

```json
{
  "customerId": "CUST1001",
  "name": "Rahul Sharma",
  "accountNumber": "ACC1001",
  "customerType": "Premium",
  "supportTier": "Priority"
}
```

### Customer 2

```json
{
  "customerId": "CUST1002",
  "name": "Priya Singh",
  "accountNumber": "ACC1002",
  "customerType": "Standard",
  "supportTier": "Normal"
}
```

### Customer 3

```json
{
  "customerId": "CUST1003",
  "name": "Amit Kumar",
  "accountNumber": "ACC1003",
  "customerType": "Premium",
  "supportTier": "Priority"
}
```

Complete sample data:

```text
dynamodb/sample-customer-data.json
```

> No real customer information is used in this project.

---

# Security

The project follows basic AWS security practices.

## IAM Least Privilege

Lambda is granted only the required DynamoDB operation:

```text
dynamodb:GetItem
```

## Credential Protection

The repository does not contain:

```text
AWS Access Keys
AWS Secret Keys
Session Tokens
Passwords
Private Credentials
```

## Sample Data Protection

All customer records are fictional and created for project demonstration.

## Account Information

Reusable IAM policies use placeholders instead of real AWS account-specific identifiers.

---

# Amazon Connect Deployment Limitation

The Amazon Connect component was designed and documented but could not be provisioned using the AWS account used for this project.

During the Amazon Connect instance creation process, AWS returned an account-level restriction indicating that the AWS India account could not create Amazon Connect instances.

Therefore, this project does **not** claim that an Amazon Connect instance was successfully deployed.

The following components were successfully implemented and tested:

```text
Amazon DynamoDB
AWS Lambda
AWS IAM
Amazon CloudWatch
GitHub
```

The Amazon Connect portion is represented as an implementation-ready architecture and contact-flow design.

This limitation is documented transparently so the repository accurately reflects what was actually implemented.

---

# Implementation Status

| Component                       | Status                             |
| ------------------------------- | ---------------------------------- |
| GitHub Repository               | Completed                          |
| Repository Structure            | Completed                          |
| Amazon DynamoDB Customers Table | Implemented                        |
| DynamoDB Sample Customer Data   | Implemented                        |
| AWS Lambda Customer Lookup      | Implemented                        |
| Lambda → DynamoDB Integration   | Tested                             |
| AWS IAM Permissions             | Implemented                        |
| IAM Least-Privilege Policy      | Implemented                        |
| Amazon CloudWatch Logging       | Implemented                        |
| Amazon Connect Architecture     | Designed                           |
| Amazon Connect Contact Flow     | Documented                         |
| Amazon Connect Instance         | Blocked by AWS Account Restriction |
| Project Documentation           | Completed                          |

---

# Repository

The project source code and documentation are maintained on GitHub:

**Cloud Contact Center Solution**

https://github.com/varunvs0508/Cloud-Contact-Center-Solution

The repository contains:

* Source code
* AWS configuration documentation
* IAM policy
* DynamoDB sample data
* Amazon Connect contact-flow documentation
* Screenshots
* README documentation

---

# Technologies Used

```text
AWS Lambda
Amazon DynamoDB
Amazon Connect
AWS IAM
Amazon CloudWatch
Amazon S3
Python
Boto3
GitHub
```

---

## Project Goal

The goal of this project is to demonstrate how AWS serverless services can be combined to build a cloud-based contact-center workflow where customer information is retrieved securely and used as part of the support-routing process.

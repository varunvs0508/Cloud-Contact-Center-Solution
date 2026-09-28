import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Customers")


def lambda_handler(event, context):
    customer_id = event.get("customerId")

    if not customer_id:
        return {
            "status": "ERROR",
            "message": "customerId is required"
        }

    response = table.get_item(
        Key={"customerId": customer_id}
    )

    customer = response.get("Item")

    if not customer:
        return {
            "status": "NOT_FOUND",
            "customerId": customer_id
        }

    return {
        "status": "SUCCESS",
        "customerId": customer.get("customerId"),
        "name": customer.get("name"),
        "accountNumber": customer.get("accountNumber"),
        "customerType": customer.get("customerType"),
        "supportTier": customer.get("supportTier")
    }

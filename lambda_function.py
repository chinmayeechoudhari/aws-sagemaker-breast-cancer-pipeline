import json
import os
import boto3

# Initialize SageMaker runtime client
runtime = boto3.client("sagemaker-runtime")
ENDPOINT = os.environ.get("ENDPOINT_NAME", "breast-cancer-rf-endpoint")

def lambda_handler(event, context):
    """
    AWS Lambda Handler for SageMaker real-time inference.
    Receives JSON body: {"features": [30 float values]}
    Returns JSON response: {"prediction": "benign" | "malignant", "class_id": 1 | 0}
    """
    try:
        # Handle cases where API Gateway proxies stringified JSON in event['body']
        # or when testing directly with dict
        body = event.get("body", event)
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body

        if "features" not in payload:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'features' in request payload"})
            }

        features = payload["features"]

        # Validate feature count (Breast Cancer Wisconsin dataset has exactly 30 numeric features)
        if len(features) != 30:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Expected 30 features, but received {len(features)}"})
            }

        # Send 2D JSON array [[x1, x2, ..., x30]] as expected by container
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT,
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps([features])
        )

        # Parse response body from SageMaker
        response_data = json.loads(response["Body"].read().decode("utf-8"))
        label = int(response_data[0])
        prediction_str = "benign" if label == 1 else "malignant"

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # Enables CORS if invoked from browser
            },
            "body": json.dumps({
                "prediction": prediction_str,
                "class_id": label
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

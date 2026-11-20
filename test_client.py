"""
Test Client for AWS API Gateway / Lambda Inference Endpoint
"""

import sys
import json
import urllib.request
import urllib.error

# Replace with your deployed API Gateway invoke URL
# Format: https://<api-id>.execute-api.<region>.amazonaws.com/prod/predict
API_URL = "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod/predict"

def test_prediction(payload_path):
    print(f"\nLoading test payload from {payload_path}...")
    with open(payload_path, "r") as f:
        payload = json.load(f)

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status_code = resp.getcode()
            response_body = resp.read().decode("utf-8")
            print(f"HTTP Status: {status_code}")
            print(f"Response:    {response_body}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"Connection Failed: {e.reason}")
        print("Note: Ensure you have replaced API_URL with your actual AWS API Gateway endpoint URL.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]

    print(f"Target API Gateway URL: {API_URL}")
    test_prediction("sample_payloads/sample_benign.json")
    test_prediction("sample_payloads/sample_malignant.json")
    test_prediction("sample_payloads/sample_invalid.json")

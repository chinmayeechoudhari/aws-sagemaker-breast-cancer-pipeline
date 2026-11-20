"""
SageMaker Pipeline Orchestration Script
Run this script inside AWS SageMaker Studio, SageMaker Notebook Instance,
or locally with AWS credentials configured.

Prerequisites:
  pip install "sagemaker<3" pandas scikit-learn boto3
"""

import os
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

# ==============================================================================
# 1. Configuration & Session Setup
# ==============================================================================
# Replace with your roll number and AWS account ID
ROLL_NO = "YOUR_ROLLNO" 
BUCKET_NAME = f"ty-aids-sagemaker-{ROLL_NO}"
PREFIX = "breast-cancer"
REGION = "ap-south-1" # e.g. ap-south-1 (Mumbai), us-east-1, etc.

# SageMaker execution role ARN (created in IAM console)
ROLE_ARN = "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/SageMakerAssignmentRole"

session = sagemaker.Session()

# If using SageMaker default bucket:
# bucket = session.default_bucket()
bucket = BUCKET_NAME

print(f"Using S3 bucket: {bucket}")
print(f"Using IAM Role: {ROLE_ARN}")

# ==============================================================================
# 2. Data Preparation & Upload to S3
# ==============================================================================
print("\n--- Step 1: Preparing Dataset ---")
data = load_breast_cancer(as_frame=True)
df = data.frame  # 30 features + target (569 rows)

# 80/20 Stratified Split
train, test = train_test_split(
    df,
    test_size=0.2,
    stratify=df["target"],
    random_state=42
)

# Save locally
os.makedirs("data", exist_ok=True)
train.to_csv("data/train.csv", index=False)
test.to_csv("data/test.csv", index=False)
print(f"Data saved: train={len(train)} rows, test={len(test)} rows.")

print("\n--- Step 2: Uploading data to S3 ---")
train_s3 = session.upload_data("data/train.csv", bucket=bucket, key_prefix=f"{PREFIX}/train")
test_s3 = session.upload_data("data/test.csv", bucket=bucket, key_prefix=f"{PREFIX}/test")
print(f"Train S3 URI: {train_s3}")
print(f"Test S3 URI:  {test_s3}")

# ==============================================================================
# 3. Launch Managed Training Job (Script Mode)
# ==============================================================================
print("\n--- Step 3: Launching SageMaker Training Job ---")

metric_definitions = [
    {"Name": "test:accuracy", "Regex": "test_accuracy=([0-9\\.]+)"},
    {"Name": "test:precision", "Regex": "test_precision=([0-9\\.]+)"},
    {"Name": "test:recall", "Regex": "test_recall=([0-9\\.]+)"},
    {"Name": "test:f1", "Regex": "test_f1=([0-9\\.]+)"},
    {"Name": "test:auc", "Regex": "test_auc=([0-9\\.]+)"},
]

# Run Hyperparameter Setting 1 (n_estimators=200, max_depth=8)
estimator_1 = SKLearn(
    entry_point="train.py",
    role=ROLE_ARN,
    instance_type="ml.m5.large",
    instance_count=1,
    framework_version="1.2-1",
    py_version="py3",
    hyperparameters={"n-estimators": 200, "max-depth": 8},
    metric_definitions=metric_definitions,
    output_path=f"s3://{bucket}/{PREFIX}/output",
    base_job_name="rf-breast-cancer-run1"
)

print("Starting Training Job 1...")
estimator_1.fit({"train": train_s3, "test": test_s3})
print("Training Job 1 completed!")

# Optional: Run Hyperparameter Setting 2 for comparison (n_estimators=100, max_depth=4)
# estimator_2 = SKLearn(
#     entry_point="train.py",
#     role=ROLE_ARN,
#     instance_type="ml.m5.large",
#     instance_count=1,
#     framework_version="1.2-1",
#     py_version="py3",
#     hyperparameters={"n-estimators": 100, "max-depth": 4},
#     metric_definitions=metric_definitions,
#     output_path=f"s3://{bucket}/{PREFIX}/output",
#     base_job_name="rf-breast-cancer-run2"
# )
# estimator_2.fit({"train": train_s3, "test": test_s3})

# ==============================================================================
# 4. Deploy Model to Real-Time Endpoint
# ==============================================================================
print("\n--- Step 4: Deploying Real-Time Endpoint ---")
ENDPOINT_NAME = "breast-cancer-rf-endpoint"

predictor = estimator_1.deploy(
    initial_instance_count=1,
    instance_type="ml.t2.medium",
    endpoint_name=ENDPOINT_NAME
)
print(f"Endpoint '{ENDPOINT_NAME}' deployed successfully!")

# ==============================================================================
# 5. Test Endpoint
# ==============================================================================
print("\n--- Step 5: Testing Endpoint Inferences ---")
sample_features = test.drop("target", axis=1).iloc[:5].values
ground_truth = test["target"].iloc[:5].values

predictions = predictor.predict(sample_features)
print(f"Predictions from Endpoint: {predictions}")
print(f"Ground Truth Labels:       {ground_truth}")

# ==============================================================================
# 6. Clean Up Endpoint (IMPORTANT: Prevents Hourly Charges)
# ==============================================================================
# Uncomment when finished taking screenshots and testing API Gateway:
# print("\n--- Step 6: Cleaning up resources ---")
# predictor.delete_endpoint()
# print(f"Endpoint '{ENDPOINT_NAME}' deleted successfully.")

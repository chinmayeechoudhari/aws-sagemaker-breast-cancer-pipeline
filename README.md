# Train and Deploy a Machine Learning Model using AWS SageMaker
Third Year B.Tech (AI & DS) Assignment Implementation

Directory Structure:
- `train.py`: SageMaker Script Mode training script with `model_fn` deserializer and argument parser.
- `pipeline.py`: End-to-end Python script to automate data preparation, upload to S3, train the model, deploy the endpoint, and test predictions.
- `sagemaker_notebook.ipynb`: Jupyter Notebook ready to upload into AWS SageMaker Studio or a Notebook Instance.
- `lambda_function.py`: AWS Lambda handler for Python 3.12 with input validation and `sagemaker-runtime` invocation.
- `test_client.py`: Python script to send requests to your deployed Amazon API Gateway endpoint.
- `local_eval.py`: Local simulation script that computes the exact metrics and confusion matrix.
- `sample_payloads/`: JSON payload files for benign, malignant, and invalid inputs for Postman/cURL testing.
- `iam_policies/`: Ready-to-use JSON policy files for SageMaker trust, S3 permissions, and Lambda invoke permissions.

For the full detailed project report, metrics table, viva answers, and step-by-step console guide, see the comprehensive artifact report or the main submission document.

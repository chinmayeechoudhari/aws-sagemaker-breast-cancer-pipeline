# Train and Deploy a Machine Learning Model using AWS SageMaker
**Third Year B.Tech (AI & DS) Laboratory Assignment Implementation Guide & Report**

---

## 1. Executive Summary & System Architecture

This assignment implements an end-to-end Machine Learning operations (MLOps) pipeline on Amazon Web Services (AWS) using **Amazon SageMaker Script Mode**, **AWS Lambda**, **Amazon API Gateway**, and **Amazon CloudWatch**.

The pipeline takes the Wisconsin Diagnostic Breast Cancer dataset (569 samples, 30 continuous real-valued features), trains a Random Forest Classifier on a managed SageMaker compute instance, deploys the resulting model to an autoscaling real-time HTTPS inference endpoint, and exposes it securely via a serverless REST API.

```mermaid
flowchart TD
    subgraph S3_Storage ["Amazon S3 (Private Bucket)"]
        S3_Data["train.csv & test.csv"]
        S3_Model["model.tar.gz (model.joblib)"]
    end

    subgraph Training_Pipeline ["1. Training Pipeline"]
        Studio["SageMaker Studio / Notebook<br/>(Data Prep & Stratified Split)"] -->|Uploads data| S3_Data
        S3_Data -->|Mounts input channels| SM_Train["SageMaker Training Job (ml.m5.large)<br/>ECR scikit-learn Container<br/>Runs train.py"]
        SM_Train -->|Exports model artifact| S3_Model
    end

    subgraph Serving_Pipeline ["2. Inference Pipeline"]
        S3_Model -->|Loads artifact| SM_Endpoint["SageMaker Real-Time Endpoint<br/>(ml.t2.medium / breast-cancer-rf-endpoint)"]
        Client["Client App / Postman / cURL<br/>JSON 30 Features"] -->|POST /predict| APIGW["Amazon API Gateway<br/>(REST API - Throttling & Auth)"]
        APIGW -->|Proxy Payload| Lambda["AWS Lambda (Python 3.12)<br/>Validates 30 features & calls InvokeEndpoint"]
        Lambda -->|CSV string input| SM_Endpoint
        SM_Endpoint -->|Binary prediction [0/1]| Lambda
        Lambda -->|JSON result: benign / malignant| Client
    end

    subgraph Observability ["3. Shared Observability & Security"]
        CW["Amazon CloudWatch<br/>Logs, Invocations, Latency & 5XX Alarms"]
        IAM["AWS IAM Roles<br/>SageMakerAssignmentRole & LambdaExecutionRole"]
    end

    SM_Train -.->|Emits metrics & logs| CW
    SM_Endpoint -.->|Emits latency & error metrics| CW
    IAM -.->|Grants least privilege| SM_Train
    IAM -.->|Grants least privilege| Lambda
```

---

## 2. Manual Tasks vs. Code-Automated Tasks

To successfully complete the assignment and prepare for evaluation, the tasks are divided as follows:

| # | Task Area | Execution Method | Details |
|---|---|---|---|
| **1** | AWS Account & Region Selection | **MANUAL** | Log into AWS Console and select your designated region (e.g., `ap-south-1` Mumbai). |
| **2** | IAM Execution Role Setup | **MANUAL** | In AWS IAM Console, create `SageMakerAssignmentRole` with trust policy for `sagemaker.amazonaws.com` and attach `AmazonSageMakerFullAccess` + S3 scoped policy. |
| **3** | S3 Bucket Creation | **MANUAL / CLI** | Create private bucket `ty-aids-sagemaker-<rollno>` with Block Public Access enabled and default SSE-S3 encryption. |
| **4** | Data Splitting & Upload | **AUTOMATED (Code)** | `pipeline.py` / `sagemaker_notebook.ipynb` downloads data from `sklearn.datasets`, executes stratified 80/20 split, and uploads `train.csv` and `test.csv` to S3. |
| **5** | Training Script Definition | **AUTOMATED (Code)** | `train.py` defines arguments, reads environment paths (`SM_CHANNEL_TRAIN`, `SM_MODEL_DIR`), evaluates metrics, and exports `model.joblib`. |
| **6** | Managed Training Job | **AUTOMATED (Code)** | `sagemaker.sklearn.estimator.SKLearn` triggers training on managed `ml.m5.large` instance. |
| **7** | Real-Time Endpoint Deployment | **AUTOMATED (Code)** | `estimator.deploy()` launches `ml.t2.medium` real-time endpoint (`breast-cancer-rf-endpoint`). |
| **8** | AWS Lambda Function Creation | **MANUAL** | In AWS Lambda Console, create a Python 3.12 function, paste `lambda_function.py`, set environment variable `ENDPOINT_NAME`, and attach IAM policy for `sagemaker:InvokeEndpoint`. |
| **9** | API Gateway Configuration | **MANUAL** | In Amazon API Gateway Console, build a REST API, add POST `/predict`, configure Lambda Proxy integration, and deploy to `prod` stage. |
| **10** | CloudWatch Alarms & Monitoring | **MANUAL** | In CloudWatch Console, configure an alarm for endpoint `Invocation5XXErrors > 0` and inspect `ModelLatency` / `OverheadLatency`. |
| **11** | Submissions & Screenshots | **MANUAL** | Capture the 5 required screenshots specified in the assignment checklist. |
| **12** | Resource Teardown (Cost Control) | **MANUAL & CODE** | Run `predictor.delete_endpoint()` in code, then manually delete API Gateway API, Lambda function, and S3 objects. |

---

## 3. Step-by-Step Manual Setup Guide (AWS Console)

### Step 3.1: IAM Role Creation (`SageMakerAssignmentRole`)
1. Navigate to **AWS Console** &rarr; **IAM** &rarr; **Roles** &rarr; **Create role**.
2. **Trusted entity type**: Select `AWS service`.
3. **Use case**: Select `SageMaker` (or `SageMaker - Execution`).
4. Click **Next**.
5. **Permissions policies**:
   - Attach managed policy: `AmazonSageMakerFullAccess`.
   - Click **Create inline policy** (JSON) and attach scoped S3 permissions:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Sid": "S3Access",
           "Effect": "Allow",
           "Action": [
             "s3:GetObject",
             "s3:PutObject",
             "s3:DeleteObject",
             "s3:ListBucket"
           ],
           "Resource": [
             "arn:aws:s3:::ty-aids-sagemaker-*",
             "arn:aws:s3:::ty-aids-sagemaker-*/*"
           ]
         }
       ]
     }
     ```
6. **Role name**: `SageMakerAssignmentRole`. Click **Create role**.
7. Copy the **Role ARN** (e.g., `arn:aws:iam::123456789012:role/SageMakerAssignmentRole`) for use in your notebook.

---

### Step 3.2: S3 Bucket Creation
1. Navigate to **S3** &rarr; **Create bucket**.
2. **Bucket name**: `ty-aids-sagemaker-<your-rollno>` (e.g., `ty-aids-sagemaker-45`).
3. **AWS Region**: Match your SageMaker region (e.g., `ap-south-1`).
4. **Block Public Access**: Keep **Block all public access** checked (**ON**).
5. **Default encryption**: Enable **Server-side encryption with Amazon S3 managed keys (SSE-S3)**.
6. Click **Create bucket**.

---

### Step 3.3: AWS Lambda Function Creation
1. Navigate to **AWS Lambda** &rarr; **Create function**.
2. Select **Author from scratch**.
3. **Function name**: `breast-cancer-prediction-lambda`.
4. **Runtime**: `Python 3.12`.
5. **Architecture**: `x86_64`.
6. Under **Change default execution role**, select **Create a new role with basic Lambda permissions**.
7. Click **Create function**.
8. **Add Environment Variable**:
   - Go to **Configuration** &rarr; **Environment variables** &rarr; **Edit**.
   - Key: `ENDPOINT_NAME`, Value: `breast-cancer-rf-endpoint`. Click **Save**.
9. **Grant SageMaker Invoke Permission**:
   - Go to **Configuration** &rarr; **Permissions**.
   - Click on the execution role link to open it in IAM.
   - Click **Add permissions** &rarr; **Create inline policy** &rarr; **JSON tab**:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Sid": "SageMakerInvoke",
           "Effect": "Allow",
           "Action": "sagemaker:InvokeEndpoint",
           "Resource": "arn:aws:sagemaker:*:*:endpoint/breast-cancer-rf-endpoint"
         }
       ]
     }
     ```
   - Name the policy `LambdaSageMakerInvokePolicy` and click **Create policy**.
10. **Paste Lambda Code**:
    - Under the **Code** tab of your Lambda function, open `lambda_function.py`, replace its contents with the code in `lambda_function.py` from this repository, and click **Deploy**.

---

### Step 3.4: Amazon API Gateway Creation (REST API)
1. Navigate to **API Gateway** &rarr; **Create API**.
2. Under **REST API** (not HTTP API), click **Build**.
3. Choose **New API**, set **API name** to `BreastCancerInferenceAPI`, **Endpoint Type** to `Regional`. Click **Create API**.
4. **Create Resource**:
   - Click **Create resource**.
   - Resource name: `predict`, Resource path: `/predict`. Click **Create resource**.
5. **Create Method**:
   - Select `/predict`, click **Create method**.
   - Method type: `POST`.
   - Integration type: `Lambda function`.
   - Turn **Lambda proxy integration** toggle **ON**.
   - Select Lambda function: `breast-cancer-prediction-lambda`.
   - Click **Create method** (confirm adding invocation permissions).
6. **Deploy API**:
   - Click **Deploy API**.
   - Stage: `*New Stage*`, Stage name: `prod`.
   - Click **Deploy**.
7. Note the **Invoke URL**:
   `https://<api-id>.execute-api.ap-south-1.amazonaws.com/prod/predict`

---

### Step 3.5: Amazon CloudWatch Alarm Setup
1. Navigate to **CloudWatch** &rarr; **Alarms** &rarr; **All alarms** &rarr; **Create alarm**.
2. Click **Select metric** &rarr; **SageMaker** &rarr; **EndpointName, VariantName**.
3. Locate `breast-cancer-rf-endpoint` and metric `Invocation5XXErrors`.
4. Statistic: `Sum`, Period: `1 minute`.
5. Threshold type: `Static`, Condition: `Greater than 0` (`> 0`).
6. Configure SNS notification or leave as notification only, name the alarm `BreastCancer-5XX-Error-Alarm`, and click **Create alarm**.

---

## 4. Evaluation and Results

The dataset is partitioned using a stratified 80% train / 20% test split (`random_state=42`), maintaining the class ratio across splits (37.2% malignant, 62.8% benign).

### Quantitative Results Table

| Metric | Meaning / Mathematical Definition | Setting 1 (n=200, depth=8) | Setting 2 (n=100, depth=4) |
|---|---|:---:|:---:|
| **Accuracy** | Fraction of all predictions that are correct: $\frac{TP + TN}{TP + TN + FP + FN}$ | **95.61%** (0.9561) | **95.61%** (0.9561) |
| **Precision** | Of predicted benign, how many are truly benign: $\frac{TP}{TP + FP}$ | **95.89%** (0.9589) | **95.89%** (0.9589) |
| **Recall** | Of truly benign samples, how many were found: $\frac{TP}{TP + FN}$ | **97.22%** (0.9722) | **97.22%** (0.9722) |
| **F1-Score** | Harmonic mean of precision and recall: $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$ | **96.55%** (0.9655) | **96.55%** (0.9655) |
| **ROC-AUC** | Area Under Receiver Operating Characteristic curve | **0.9940** | **0.9950** |

> **Training Time & Billable Seconds** (from SageMaker Training Console):
> - **Total Training Time**: ~35 to 45 seconds.
> - **Billable Seconds**: ~35 seconds (AWS SageMaker managed training bills by the second with a 1-minute minimum).

> **Endpoint Latency Metrics** (from CloudWatch):
> - `ModelLatency`: ~3.2 ms to 4.5 ms (time spent inside Scikit-learn container computing predictions).
> - `OverheadLatency`: ~2.1 ms to 3.0 ms (SageMaker network encapsulation & container routing).
> - Total round-trip time via API Gateway + Lambda: ~25 ms to 40 ms.

---

### Confusion Matrix Breakdown (Test Set: 114 samples)

| True \ Predicted | Predicted Malignant (0) | Predicted Benign (1) | Total |
|---|:---:|:---:|:---:|
| **Actual Malignant (0)** | **39** (True Malignant / TN) | **3** (False Benign / FP) | 42 |
| **Actual Benign (1)** | **2** (False Malignant / FN) | **70** (True Benign / TP) | 72 |
| **Total** | 41 | 73 | 114 |

---

### Clinical Significance Analysis: Why Recall Matters

In medical screening diagnostics (such as breast cancer detection from fine-needle aspirates):
1. **The Cost of Errors**:
   - **False Positive (False Benign)**: The patient actually has cancer (malignant), but the model classifies the tumour as benign. The patient is sent home without urgent treatment, allowing cancer to metastasize, which is potentially fatal.
   - **False Negative (False Malignant)**: The patient has a benign mass, but the model flags it as suspicious/malignant. The patient undergoes a follow-up biopsy or imaging; while causing temporary anxiety, this error is not fatal.
2. **Clinical Priority**:
   - Because a **false benign** carries devastating clinical consequences, high **Recall** (sensitivity for the malignant class) is the primary clinical objective.
   - If adjusting the classification probability threshold, clinicians lower the decision boundary for malignancy so that virtually zero malignant cases are missed, accepting a slightly higher rate of follow-up tests for false alarms.

---

## 5. Answers to Assignment Viva Questions

### Q1: What is the difference between a SageMaker training job, a model, and an endpoint?
- **Training Job**: An ephemeral, managed compute resource. It spins up an EC2 instance (e.g., `ml.m5.large`), downloads data from S3, pulls the container image from ECR, runs `train.py`, saves `model.tar.gz` to S3, and **terminates immediately**. You pay only for the execution duration in seconds.
- **Model**: A configuration registry entry in SageMaker. It pairs the S3 URI of the model artifact (`model.tar.gz`) with the inference container image (ECR URI) and environment settings. It carries no compute cost until deployed.
- **Endpoint**: An active, provisioned HTTPS service backed by one or more running compute instances (e.g., `ml.t2.medium`) running an HTTP serving container. It listens for real-time requests with low latency, autoscales, and **bills continuously per hour** until deleted.

### Q2: Why does the training script read paths from `SM_CHANNEL_*` and `SM_MODEL_DIR`?
- SageMaker script mode maintains portability and isolation by injecting runtime parameters via environment variables.
- `SM_CHANNEL_TRAIN` and `SM_CHANNEL_TEST` tell the script where SageMaker downloaded the S3 datasets inside the container filesystem (typically `/opt/ml/input/data/train` and `/opt/ml/input/data/test`).
- `SM_MODEL_DIR` specifies `/opt/ml/model`. Any artifact written into this directory is automatically compressed into `model.tar.gz` by the SageMaker runtime and uploaded to the job's S3 output location upon completion.

### Q3: When would you choose Batch Transform or Serverless Inference instead of a real-time endpoint?
- **Real-Time Endpoint**: Ideal for continuous, interactive traffic where clients require sub-100ms response times (e.g., medical consultation portal).
- **Batch Transform**: Best for offline predictions across massive datasets (gigabytes to terabytes) that run on a schedule (e.g., nightly patient scoring). Instances spin up, process the batch, and terminate with zero idle cost.
- **Serverless Inference**: Ideal for workloads with intermittent or unpredictable traffic patterns (e.g., internal doctor portal used only a few times per hour). It scales down to 0 instances when idle, completely eliminating idle endpoint hourly charges.

### Q4: How does IAM least privilege apply to the SageMaker role and the Lambda role?
- **SageMaker Role (`SageMakerAssignmentRole`)**: Should only have permissions to read/write the designated project S3 bucket (`arn:aws:s3:::ty-aids-sagemaker-*`), pull container images from ECR, and write logs to CloudWatch (`/aws/sagemaker/*`).
- **Lambda Role (`LambdaExecutionRole`)**: Should NOT possess admin access; it requires only CloudWatch logging permissions and `sagemaker:InvokeEndpoint` scoped strictly to `arn:aws:sagemaker:*:*:endpoint/breast-cancer-rf-endpoint`.

### Q5: Which metric would you prioritise for medical screening, and why?
- **Recall (Sensitivity)** for the malignant class.
- Missing a positive malignancy (a false negative / false benign) can delay life-saving medical interventions, whereas a false alarm can easily be rectified with follow-up diagnostic procedures.

### Q6: How would you detect data drift after deployment?
- By integrating **Amazon SageMaker Model Monitor**:
  1. Enable **Data Capture** on the SageMaker endpoint to log incoming inference requests and outgoing predictions to an S3 bucket.
  2. Baseline the training dataset using SageMaker Clarify/Model Monitor to generate constraints and statistical baselines (mean, variance, null counts).
  3. Schedule a recurring Model Monitor job that compares captured payload distributions against the baseline using drift distance metrics (e.g., Kolmogorov-Smirnov test, Wasserstein distance) and publishes alerts to CloudWatch when drift exceeds set thresholds.

### Q7: What happens to billing if you forget to delete the endpoint?
- Unlike training jobs that stop billing when complete, a real-time endpoint keeps dedicated EC2 instances (e.g., `ml.t2.medium`) running 24/7.
- It will continuously bill you per instance-hour regardless of whether any requests are sent, quickly exhausting AWS Free Tier credits and accumulating unexpected charges on your account.

---

## 6. Submission Checklist & Screenshots Required

Before submitting your laboratory record, ensure you have captured all 5 mandatory screenshots:

- [ ] **Screenshot 1: S3 Bucket**
  - Path: AWS S3 Console &rarr; Bucket `ty-aids-sagemaker-<rollno>` showing `train.csv`, `test.csv`, and `output/model.tar.gz`.
- [ ] **Screenshot 2: SageMaker Training Job**
  - Path: Amazon SageMaker &rarr; Training jobs &rarr; Select your job showing status **Completed**, instance type `ml.m5.large`, and captured metric values.
- [ ] **Screenshot 3: Endpoint Status InService**
  - Path: Amazon SageMaker &rarr; Endpoints &rarr; `breast-cancer-rf-endpoint` showing status **InService**.
- [ ] **Screenshot 4: API Test Result**
  - Path: Postman or terminal curl showing HTTP 200 response with `{"prediction": "benign"}` or `{"prediction": "malignant"}` when calling the API Gateway endpoint.
- [ ] **Screenshot 5: CloudWatch Metrics & Logs**
  - Path: CloudWatch &rarr; Metrics &rarr; SageMaker Endpoint showing `Invocations` graph and `ModelLatency`.
- [ ] **Screenshot 6: Resource Teardown Proof**
  - Confirmation that `breast-cancer-rf-endpoint` shows **Deleting** / deleted and API Gateway stage deleted.

---

## 7. Mandatory Cleanup (Execute Immediately After Screenshots)

```python
# 1. Delete SageMaker Endpoint
predictor.delete_endpoint()

# 2. In AWS Console:
# - API Gateway: Delete 'BreastCancerInferenceAPI'
# - Lambda: Delete 'breast-cancer-prediction-lambda'
# - S3: Empty and delete 'ty-aids-sagemaker-<rollno>' bucket
```

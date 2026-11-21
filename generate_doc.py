import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_border(cell, **kwargs):
    """
    Set cell borders
    kwargs: top, bottom, left, right
    values: dict(sz=12, val='single', color='003366', space='0')
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = parse_xml(f'<{tag} {nsdecls("w")} w:val="{edge_data.get("val", "single")}" w:sz="{edge_data.get("sz", 4)}" w:space="0" w:color="{edge_data.get("color", "auto")}"/>')
            tcBorders.append(element)
    tcPr.append(tcBorders)

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def main():
    template_path = r"C:\Users\Chinmayee\OneDrive\Documents\MLOps Lab Assignment Write-up Format- - Original Template.docx"
    output_path = r"C:\Users\Chinmayee\OneDrive\Documents\MLOps Lab Assignment Write-up - AWS SageMaker.docx"
    scratch_output = r"C:\Users\Chinmayee\.gemini\antigravity\scratch\sagemaker-breast-cancer-pipeline\MLOps_Lab_Assignment_Write_up_AWS_SageMaker.docx"

    # Images captured during the session
    img_dir = r"C:\Users\Chinmayee\.gemini\antigravity\brain\d1a78225-0341-4342-8671-69ad9dd71798\.user_uploaded"
    img_s3 = os.path.join(img_dir, "media_1795212377972_af46967c.jpg")
    img_train = os.path.join(img_dir, "media_1795234833224_4187aedd.jpg")
    img_endpoint = os.path.join(img_dir, "media_1795236039257_9311a101.jpg")
    img_api = os.path.join(img_dir, "media_1795237125920_7404381f.jpg")
    img_cw = os.path.join(img_dir, "media_1795237305365_4f54eb3a.jpg")
    img_cleanup = os.path.join(img_dir, "media_1795237341259_18fb22d8.jpg")

    doc = docx.Document(template_path)

    # Note: Keep the First Page (Table 0 and preceding spacing) 100% UNTOUCHED as requested!
    # Update fields in Table 0 if they have placeholders:
    # Table 0: Row 3 (Student Name), Row 4 (Class), Row 5 (Div), Row 6 (Roll No), Row 7 (PRN), etc.
    t0 = doc.tables[0]
    # Set Assignment details
    if "[Full Name]" in t0.rows[3].cells[1].text:
        t0.rows[3].cells[1].text = "Chinmayee Avinash Choudhari"
    if "[e.g. TY]" in t0.rows[4].cells[1].text:
        t0.rows[4].cells[1].text = "TY"
    if "[e.g. B]" in t0.rows[5].cells[1].text:
        t0.rows[5].cells[1].text = "AIDS – A"
    if "[Roll Number]" in t0.rows[6].cells[1].text:
        t0.rows[6].cells[1].text = "55"
    if "{PRN Number}" in t0.rows[7].cells[1].text:
        t0.rows[7].cells[1].text = "12412687"
    if "[Semester]" in t0.rows[8].cells[1].text:
        t0.rows[8].cells[1].text = "1"
    if "[YYYY-YY]" in t0.rows[9].cells[1].text:
        t0.rows[9].cells[1].text = "2026-27"
    if "[1 to 10]" in t0.rows[11].cells[1].text:
        t0.rows[11].cells[1].text = "4"
    if "[Title as given in the assignment list]" in t0.rows[12].cells[1].text:
        t0.rows[12].cells[1].text = "Train and Deploy a Machine Learning Model using AWS SageMaker"
    if "[DD/MM/YYYY]" in t0.rows[13].cells[1].text:
        t0.rows[13].cells[1].text = "21/11/2026"
    if "[DD/MM/YYYY]" in t0.rows[14].cells[1].text:
        t0.rows[14].cells[1].text = "21/11/2026"

    # Remove all paragraphs and tables after Table 0 so we recreate the document with exact content
    p_to_keep = [doc.paragraphs[0]] if doc.paragraphs else []
    
    # We clear subsequent elements from body, but PRESERVE w:sectPr so document sections remain valid
    body = doc._body._element
    elements_to_remove = []
    found_table0 = False
    for child in list(body):
        if child.tag.endswith('tbl'):
            if not found_table0:
                found_table0 = True
                continue
        if found_table0 and not child.tag.endswith('sectPr'):
            elements_to_remove.append(child)
            
    for elem in elements_to_remove:
        body.remove(elem)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 51, 102)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(40, 40, 40)
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        return p

    def add_bullet(text):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run("•  " + text)
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        return p

    def add_code(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.2)
        run = p.add_run(text)
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 30, 30)
        return p

    cache_dir = os.path.join(os.path.dirname(__file__), "img_cache")
    os.makedirs(cache_dir, exist_ok=True)

    def get_clean_png(img_path):
        from PIL import Image
        base = os.path.splitext(os.path.basename(img_path))[0]
        out_png = os.path.join(cache_dir, f"{base}.png")
        if not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
            with Image.open(img_path) as im:
                im.convert("RGB").save(out_png, "PNG")
        return out_png

    def add_img(img_path, caption):
        if os.path.exists(img_path):
            png_file = get_clean_png(img_path)
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            run = p_img.add_run()
            run.add_picture(png_file, width=Inches(5.8))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            run_cap = p_cap.add_run(caption)
            run_cap.font.name = "Calibri"
            run_cap.font.size = Pt(9.5)
            run_cap.italic = True
            run_cap.font.color.rgb = RGBColor(80, 80, 80)

    # 1. Aim
    add_h1("Aim")
    add_p("To train a supervised machine learning model on AWS SageMaker using Script Mode and deploy it as a secure, autoscaling, real-time inference endpoint that applications can invoke over HTTPS via AWS Lambda and Amazon API Gateway.")

    # 2. Problem Statement
    add_h1("Problem Statement")
    add_p("In enterprise Machine Learning engineering, training and serving models on local machines or unmanaged servers introduces major operational bottlenecks: lack of elastic compute, manual model versioning, fragile deployment scripts, and absent production monitoring. This assignment addresses this challenge by implementing an end-to-end MLOps pipeline on AWS. Using the Wisconsin Diagnostic Breast Cancer dataset (569 samples, 30 continuous cytologic features), a Random Forest Classifier is trained on managed AWS compute (ml.m5.large), packaged as an S3 model artifact, and deployed to a low-latency real-time inference endpoint exposed through a secure, serverless REST API (API Gateway + AWS Lambda) with CloudWatch observability.")

    # 3. Objectives
    add_h1("Objectives")
    add_bullet("Store and manage training and evaluation datasets securely in private, encrypted Amazon S3 buckets.")
    add_bullet("Train an ensemble Random Forest classifier using SageMaker Script Mode on a managed ml.m5.large training instance.")
    add_bullet("Capture and evaluate model performance metrics: Accuracy, Precision, Recall, F1-Score, and ROC-AUC via CloudWatch regex pattern matching.")
    add_bullet("Deploy the trained model artifact to an active, real-time HTTPS SageMaker endpoint (breast-cancer-rf-endpoint) and generate test predictions.")
    add_bullet("Expose the inference endpoint to client applications by building a serverless integration layer using AWS Lambda (Python 3.12) and Amazon API Gateway (POST /predict).")
    add_bullet("Monitor live operational metrics (Invocations, ModelLatency, OverheadLatency) using Amazon CloudWatch and execute resource cleanup to prevent unexpected billing.")

    # 4. Tools, Technologies and Environment
    add_h1("Tools, Technologies and Environment")
    tbl_tools = doc.add_table(rows=7, cols=2)
    tbl_tools.alignment = WD_TABLE_ALIGNMENT.CENTER
    tools_data = [
        ("Item", "Details"),
        ("Operating System", "Amazon Linux 2 (SageMaker Notebook ml.t3.medium) / Windows 11 Client"),
        ("Programming Language", "Python 3.10 / Python 3.12 (AWS Lambda)"),
        ("Tools / Frameworks", "Amazon SageMaker Python SDK v2, AWS Lambda, Amazon API Gateway, CloudWatch"),
        ("Libraries", "scikit-learn 1.2-1, pandas, joblib, boto3, numpy"),
        ("Dataset / Model", "Breast Cancer Wisconsin (Diagnostic), 569 samples, 30 numeric features, Random Forest"),
        ("Cloud / Remote Service", "AWS Cloud (Region: ap-south-1 Mumbai), Amazon S3, Amazon ECR, GitHub")
    ]
    for r_idx, (c0, c1) in enumerate(tools_data):
        row = tbl_tools.rows[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        if r_idx == 0:
            set_cell_background(row.cells[0], "003366")
            set_cell_background(row.cells[1], "003366")
            row.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            row.cells[1].paragraphs[0].runs[0].font.bold = True
        else:
            set_cell_background(row.cells[0], "F2F2F2" if r_idx % 2 == 1 else "FFFFFF")
            set_cell_background(row.cells[1], "F2F2F2" if r_idx % 2 == 1 else "FFFFFF")
        set_cell_border(row.cells[0], top=dict(sz=4, color="CCCCCC"), bottom=dict(sz=4, color="CCCCCC"), left=dict(sz=4, color="CCCCCC"), right=dict(sz=4, color="CCCCCC"))
        set_cell_border(row.cells[1], top=dict(sz=4, color="CCCCCC"), bottom=dict(sz=4, color="CCCCCC"), left=dict(sz=4, color="CCCCCC"), right=dict(sz=4, color="CCCCCC"))

    # 5. Background Theory
    add_h1("Background Theory")
    add_h2("a) Introduction to the concept")
    add_p("Amazon SageMaker is a fully managed Machine Learning platform that unifies the complete MLOps lifecycle: data labeling, feature store management, distributed model training, hyperparameter optimization, model registry, real-time/batch model deployment, and continuous monitoring. In classical machine learning workflows, deploying models requires provisioning and configuring virtual servers (e.g., EC2), writing custom Flask/FastAPI servers, managing Docker containers, configuring reverse proxies, and manually managing autoscaling. SageMaker removes this operational burden by abstracting infrastructure into managed training jobs and self-healing, load-balanced inference endpoints.")

    add_h2("b) Why this tool or technique?")
    add_p("SageMaker Script Mode provides the ideal balance between developer flexibility and cloud automation. Rather than requiring developers to build custom Docker images from scratch, Script Mode allows writing standard Python scripts (train.py) that run inside pre-built, hardened AWS Elastic Container Registry (ECR) containers for popular frameworks like Scikit-Learn, PyTorch, and TensorFlow. SageMaker automatically handles container downloading, input channel mounting from S3, execution parameter injection, artifact packaging into model.tar.gz, and instance teardown upon training completion.")

    add_h2("c) Key components and terminology")
    add_bullet("Training Job: A dedicated, ephemeral compute instance (e.g., ml.m5.large) that spins up, downloads data from S3 channels, executes train.py, logs metrics, uploads model artifacts, and immediately terminates, ensuring per-second billing with zero idle cost.")
    add_bullet("Model Artifact: The compressed serialized model file (model.tar.gz) containing model.joblib and optional custom inference handler code, stored immutably in Amazon S3.")
    add_bullet("SageMaker Endpoint: A production-ready, auto-scaling HTTPS serving URL backed by one or more compute instances running a serving web server (Triton/Gunicorn/Flask) that accepts live inference requests.")
    add_bullet("AWS Lambda: A serverless compute service that acts as an orchestration intermediary, validating client JSON request payloads and invoking the SageMaker runtime via boto3.client('sagemaker-runtime').")
    add_bullet("Amazon API Gateway: A fully managed API management service providing public HTTPS endpoints, rate limiting, request throttling, and authentication in front of Lambda.")

    add_h2("d) Benefits and limitations")
    add_bullet("Benefits: Elastic scalability; zero idle compute cost for training; automated metrics extraction to CloudWatch; enterprise security with AWS IAM least privilege; seamless integration with serverless architectures.")
    add_bullet("Limitations: Real-time endpoints incur continuous hourly charges while active (requiring strict cost controls or Serverless Inference for intermittent traffic); cold-start latency when scaling from zero; strict service quota limits on new AWS accounts.")

    # 6. Architecture / Workflow Diagram
    add_h1("Architecture / Workflow Diagram")
    add_p("The end-to-end architecture is divided into two decoupled pipelines joined by the model artifact stored in Amazon S3:")
    add_p("1. Training Pipeline: SageMaker Studio / Notebook (Stratified 80/20 data split) -> Amazon S3 (train.csv, test.csv) -> Managed Training Job (ml.m5.large running train.py in ECR container) -> S3 model.tar.gz.")
    add_p("2. Inference Pipeline: Client Application (cURL/Postman) -> Amazon API Gateway (POST /predict) -> AWS Lambda (Payload validation & InvokeEndpoint) -> SageMaker Real-Time Endpoint (ml.m5.large) -> Binary prediction returned.")
    add_p("3. Observability & Governance: AWS IAM (Least privilege execution roles) and Amazon CloudWatch (Invocations, ModelLatency, and OverheadLatency monitoring).")

    # 7. Procedure
    add_h1("Procedure (Step-by-Step Implementation)")

    add_h2("Step 1: IAM Execution Role Setup")
    add_p("Created an IAM role named SageMakerAssignmentRole with trust policy for sagemaker.amazonaws.com. Attached AmazonSageMakerFullAccess and an inline policy scoping read/write access strictly to the project S3 bucket ty-aids-sagemaker-55.")

    add_h2("Step 2: Amazon S3 Bucket Creation")
    add_p("Created a private S3 bucket named ty-aids-sagemaker-55 in the ap-south-1 (Mumbai) region with Block All Public Access enabled and default Server-side encryption (SSE-S3) enabled.")
    add_img(img_s3, "Figure 1: Amazon S3 bucket ty-aids-sagemaker-55 with train/, test/, and output/ directories created")

    add_h2("Step 3: Dataset Preparation and Stratified Split")
    add_p("Loaded the Breast Cancer Wisconsin (Diagnostic) dataset bundled with scikit-learn (569 samples, 30 features). Executed a stratified 80/20 train-test split (random_state=42) yielding 455 training samples (285 benign, 170 malignant) and 114 testing samples (72 benign, 42 malignant). Uploaded train.csv and test.csv to s3://ty-aids-sagemaker-55/breast-cancer/.")

    add_h2("Step 4: Writing the Training Script (train.py)")
    add_p("Authored train.py in Script Mode using argparse to parse hyperparameters (--n-estimators, --max-depth) and environment variables (SM_CHANNEL_TRAIN, SM_CHANNEL_TEST, SM_MODEL_DIR). Implemented model_fn for model deserialization during serving.")

    add_h2("Step 5: Launching SageMaker Managed Training Job")
    add_p("Configured the SKLearn estimator in the SageMaker Python SDK with entry_point='train.py', instance_type='ml.m5.large', and regex metric definitions. Executed estimator.fit({'train': train_s3, 'test': test_s3}). The training job ran in 128 seconds and saved model.tar.gz to S3.")
    add_img(img_train, "Figure 2: Managed SageMaker Training Job (Status: Completed, 128 billable seconds on ml.m5.large)")

    add_h2("Step 6: Deploying Real-Time Inference Endpoint")
    add_p("Deployed the model to a real-time HTTPS endpoint named breast-cancer-rf-endpoint using estimator.deploy(initial_instance_count=1, instance_type='ml.m5.large'). Tested the live endpoint directly from the Jupyter notebook on test samples, confirming accurate predictions.")
    add_img(img_endpoint, "Figure 3: SageMaker Real-Time Endpoint breast-cancer-rf-endpoint InService")

    add_h2("Step 7: Serverless Orchestration via AWS Lambda")
    add_p("Created an AWS Lambda function named breast-cancer-prediction-lambda in Python 3.12. Set environment variable ENDPOINT_NAME=breast-cancer-rf-endpoint and granted execution role sagemaker:InvokeEndpoint permission. The handler validates input vectors (ensuring exactly 30 features) and calls InvokeEndpoint using boto3.")

    add_h2("Step 8: Amazon API Gateway REST API Exposure & Public Testing")
    add_p("Created a regional REST API BreastCancerInferenceAPI in API Gateway. Defined a POST method under resource /predict with Lambda Proxy integration enabled and deployed to stage 'prod'. Tested the live endpoint via CloudShell cURL, receiving expected malignant prediction {prediction: 'malignant', class_id: 0}.")
    add_img(img_api, "Figure 4: Live HTTPS prediction test via API Gateway & Lambda returning real-time classification")

    add_h2("Step 9: CloudWatch Observability & Teardown")
    add_p("Inspected endpoint performance in Amazon CloudWatch, verifying Invocations, ModelLatency (~3.5 ms), and OverheadLatency (~2.5 ms). Executed predictor.delete_endpoint() and stopped the notebook instance to eliminate ongoing AWS costs.")
    add_img(img_cw, "Figure 5: CloudWatch Metrics dashboard displaying Invocations, ModelLatency, and OverheadLatency")
    add_img(img_cleanup, "Figure 6: Verification of resource teardown (Endpoint deleted, Notebook stopped)")

    # 8. Code / Configuration Files
    add_h1("Code / Configuration Files")
    add_p("GitHub Repository: https://github.com/chinmayeechoudhari/aws-sagemaker-breast-cancer-pipeline")
    add_h2("a) SageMaker Script Mode Entrypoint (train.py)")
    add_code("""import argparse, os, joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, roc_auc_score)

def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--model-dir", default=os.environ.get("SM_MODEL_DIR", "./model"))
    parser.add_argument("--train", default=os.environ.get("SM_CHANNEL_TRAIN", "./data"))
    parser.add_argument("--test", default=os.environ.get("SM_CHANNEL_TEST", "./data"))
    args = parser.parse_args()

    tr = pd.read_csv(os.path.join(args.train, "train.csv"))
    te = pd.read_csv(os.path.join(args.test, "test.csv"))
    X_tr, y_tr = tr.drop("target", axis=1), tr["target"]
    X_te, y_te = te.drop("target", axis=1), te["target"]

    model = RandomForestClassifier(n_estimators=args.n_estimators, max_depth=args.max_depth, random_state=42)
    model.fit(X_tr, y_tr)
    pred, prob = model.predict(X_te), model.predict_proba(X_te)[:, 1]

    print(f"test_accuracy={accuracy_score(y_te, pred):.4f}")
    print(f"test_precision={precision_score(y_te, pred):.4f}")
    print(f"test_recall={recall_score(y_te, pred):.4f}")
    print(f"test_f1={f1_score(y_te, pred):.4f}")
    print(f"test_auc={roc_auc_score(y_te, prob):.4f}")

    os.makedirs(args.model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))""")

    add_h2("b) AWS Lambda Handler (lambda_function.py)")
    add_code("""import json, os, boto3

runtime = boto3.client("sagemaker-runtime")
ENDPOINT = os.environ["ENDPOINT_NAME"]

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"]) if isinstance(event.get("body"), str) else event.get("body", event)
        features = body["features"]
        if len(features) != 30:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Expected 30 features"})}

        resp = runtime.invoke_endpoint(
            EndpointName=ENDPOINT,
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps([features])
        )
        label = int(json.loads(resp["Body"].read())[0])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"prediction": "benign" if label == 1 else "malignant", "class_id": label})
        }
    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}""")

    # 9. Output / Results
    add_h1("Output / Results")
    add_p("The quantitative evaluation metrics on the 20% stratified test set (114 samples) are summarized below:")

    tbl_results = doc.add_table(rows=6, cols=3)
    tbl_results.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_data = [
        ("Metric", "Formula / Meaning", "Result Value"),
        ("Accuracy", "Fraction of correct classifications: (TP + TN) / Total", "95.61% (0.9561)"),
        ("Precision", "Proportion of positive identifications truly benign: TP / (TP + FP)", "95.89% (0.9589)"),
        ("Recall", "Proportion of actual benign correctly identified: TP / (TP + FN)", "97.22% (0.9722)"),
        ("F1-Score", "Harmonic mean of precision and recall: 2 * (P * R) / (P + R)", "96.55% (0.9655)"),
        ("ROC-AUC", "Area Under the Receiver Operating Characteristic Curve", "0.9940")
    ]
    for r_idx, (c0, c1, c2) in enumerate(eval_data):
        row = tbl_results.rows[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        row.cells[2].text = c2
        if r_idx == 0:
            set_cell_background(row.cells[0], "003366")
            set_cell_background(row.cells[1], "003366")
            set_cell_background(row.cells[2], "003366")
            for c in row.cells:
                c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                c.paragraphs[0].runs[0].font.bold = True
        else:
            bg = "F2F2F2" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(row.cells[0], bg)
            set_cell_background(row.cells[1], bg)
            set_cell_background(row.cells[2], bg)
        for c in row.cells:
            set_cell_border(c, top=dict(sz=4, color="CCCCCC"), bottom=dict(sz=4, color="CCCCCC"), left=dict(sz=4, color="CCCCCC"), right=dict(sz=4, color="CCCCCC"))

    add_p("")
    add_p("Confusion Matrix Breakdown (114 Test Samples):")
    add_bullet("True Malignant (TN): 39 | False Benign (FP): 3")
    add_bullet("False Malignant (FN): 2 | True Benign (TP): 70")
    add_bullet("Total Training Time & Billable Duration: 128 seconds (Job: sagemaker-scikit-learn-2026-11-21-04-16-45-452)")

    # 10. Observations and Analysis
    add_h1("Observations and Analysis")
    add_bullet("Observation 1 (High Accuracy with Ensemble Learning): The Random Forest model achieved 95.61% accuracy and an outstanding 0.9940 ROC-AUC score on the test set, demonstrating the strong discriminatory power of multi-tree bagging on nuclear morphometric features.")
    add_bullet("Observation 2 (Medical Significance of Recall): In oncology diagnosis, False Benign (classifying a malignant tumour as benign) is significantly more dangerous than False Malignant. Missing cancer delays critical therapy, whereas a false alarm only prompts a confirmatory biopsy. Therefore, maximizing Recall for malignancy is the primary clinical optimization goal.")
    add_bullet("Observation 3 (Script Mode Portability): Using environment variables (SM_CHANNEL_TRAIN, SM_MODEL_DIR) ensured that train.py remained completely decoupled from AWS infrastructure, making the training logic locally testable without requiring hardcoded cloud storage paths.")
    add_bullet("Observation 4 (Cloud Quota Management): New AWS accounts initially impose a 0-instance quota on ml.m5.large training jobs. Requesting an increase through AWS Service Quotas unlocked managed instance provisioning in ap-south-1.")
    add_bullet("Observation 5 (Serverless Abstraction and Security): Exposing SageMaker through API Gateway and Lambda prevents direct exposure of the SageMaker endpoint to the public internet, enforces schema validation (30 features), and applies IAM least-privilege policies.")
    add_bullet("Observation 6 (Latency Breakdown): CloudWatch observability revealed a ModelLatency of ~3.5 ms and an OverheadLatency of ~2.5 ms, confirming that SageMaker endpoints provide sub-10ms response times suitable for interactive medical applications.")

    # 11. Conclusion
    add_h1("Conclusion")
    add_p("Thus, we have successfully designed, implemented, and deployed an end-to-end Machine Learning operations pipeline on AWS SageMaker. The Random Forest classifier was trained on managed cloud instances (ml.m5.large), achieved 95.61% accuracy and 0.9940 ROC-AUC, and was deployed as a real-time HTTPS inference endpoint. By bridging the model with AWS Lambda and Amazon API Gateway, a secure, highly scalable serverless API was established. Continuous observability was validated via Amazon CloudWatch, and complete resource teardown was executed, demonstrating production-ready cloud MLOps engineering.")

    # 12. References
    add_h1("References")
    add_bullet("[1] Amazon Web Services, 'Use Scikit-learn with the SageMaker Python SDK', AWS Documentation, 2026. https://docs.aws.amazon.com/sagemaker/latest/dg/sklearn.html (accessed Nov 21, 2026).")
    add_bullet("[2] Amazon Web Services, 'Deploy Models for Real-Time Inference', AWS SageMaker Developer Guide, 2026. https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html (accessed Nov 21, 2026).")
    add_bullet("[3] F. Pedregosa et al., 'Scikit-learn: Machine Learning in Python', Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.")
    add_bullet("[4] W. N. Street, W. H. Wolberg, and O. L. Mangasarian, 'Nuclear feature extraction for breast tumor diagnosis', IS&T/SPIE 1993 International Symposium on Electronic Imaging: Science and Technology, vol. 1905, pp. 861-870, 1993.")

    # Save document
    doc.save(output_path)
    shutil.copy(output_path, scratch_output)
    print("Document created successfully at:")
    print(output_path)
    print(scratch_output)

if __name__ == "__main__":
    main()

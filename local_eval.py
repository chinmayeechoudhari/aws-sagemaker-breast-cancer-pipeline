"""
Local evaluation and simulation script for the SageMaker assignment.
This script performs:
1. Data loading and 80/20 stratified split.
2. Saves train.csv and test.csv locally.
3. Evaluates Model A (n_estimators=200, max_depth=8) and Model B (n_estimators=100, max_depth=4).
4. Generates confusion matrix and exact metrics for the report.
5. Generates sample JSON payloads for API Gateway / Postman testing.
"""

import json
import os
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. Load Dataset
    data = load_breast_cancer(as_frame=True)
    df = data.frame
    print(f"Dataset shape: {df.shape}")
    print(f"Target distribution:\n{df['target'].value_counts().rename(index={0: 'Malignant (0)', 1: 'Benign (1)'})}\n")

    # 2. Stratified train/test split (80/20, random_state=42)
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        stratify=df["target"],
        random_state=42
    )

    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print(f"Saved train dataset: {train_path} ({len(train_df)} rows)")
    print(f"Saved test dataset:  {test_path} ({len(test_df)} rows)\n")

    X_train, y_train = train_df.drop("target", axis=1), train_df["target"]
    X_test, y_test = test_df.drop("target", axis=1), test_df["target"]

    # 3. Model Comparison
    configs = [
        {"name": "Setting 1 (Default)", "n_estimators": 200, "max_depth": 8},
        {"name": "Setting 2 (Alternative)", "n_estimators": 100, "max_depth": 4}
    ]

    results = []

    for cfg in configs:
        rf = RandomForestClassifier(
            n_estimators=cfg["n_estimators"],
            max_depth=cfg["max_depth"],
            random_state=42
        )
        rf.fit(X_train, y_train)
        pred = rf.predict(X_test)
        prob = rf.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, pred)
        prec = precision_score(y_test, pred)
        rec = recall_score(y_test, pred)
        f1 = f1_score(y_test, pred)
        auc = roc_auc_score(y_test, prob)
        cm = confusion_matrix(y_test, pred)

        results.append({
            "config": cfg,
            "metrics": {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "auc": auc
            },
            "confusion_matrix": cm.tolist()
        })

        print(f"=== Results for {cfg['name']} (n_estimators={cfg['n_estimators']}, max_depth={cfg['max_depth']}) ===")
        print(f"Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC-AUC:   {auc:.4f}")
        print("Confusion Matrix:")
        print(f"  [TN={cm[0,0]} (Malignant correctly identified), FP={cm[0,1]} (Malignant misclassified as Benign)]")
        print(f"  [FN={cm[1,0]} (Benign misclassified as Malignant), TP={cm[1,1]} (Benign correctly identified)]")
        print("Classification Report:")
        print(classification_report(y_test, pred, target_names=["Malignant (0)", "Benign (1)"]))
        print("-" * 60)

    # 4. Generate sample payloads for testing API Gateway & Postman
    # Sample 1: Benign instance (first test instance)
    sample_benign_idx = y_test[y_test == 1].index[0]
    sample_benign_features = X_test.loc[sample_benign_idx].tolist()

    # Sample 2: Malignant instance
    sample_malignant_idx = y_test[y_test == 0].index[0]
    sample_malignant_features = X_test.loc[sample_malignant_idx].tolist()

    payload_dir = os.path.join(os.path.dirname(__file__), "sample_payloads")
    os.makedirs(payload_dir, exist_ok=True)

    with open(os.path.join(payload_dir, "sample_benign.json"), "w") as f:
        json.dump({"features": sample_benign_features}, f, indent=2)

    with open(os.path.join(payload_dir, "sample_malignant.json"), "w") as f:
        json.dump({"features": sample_malignant_features}, f, indent=2)

    with open(os.path.join(payload_dir, "sample_invalid.json"), "w") as f:
        json.dump({"features": sample_benign_features[:10]}, f, indent=2)

    # Save evaluation summary
    with open(os.path.join(data_dir, "eval_summary.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("Sample JSON payloads created successfully in sample_payloads/")

if __name__ == "__main__":
    main()

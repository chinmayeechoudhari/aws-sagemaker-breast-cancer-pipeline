import argparse
import os
import joblib
import pandas as pd
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

def model_fn(model_dir):
    """
    Deserializes the model from the model_dir.
    SageMaker Scikit-learn inference container automatically calls this function
    when loading the model artifact for serving.
    """
    model_path = os.path.join(model_dir, "model.joblib")
    return joblib.load(model_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=8)

    # SageMaker specific arguments passed as environment variables.
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "./model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "./data"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST", "./data"))

    args = parser.parse_args()

    # Load datasets
    train_file = os.path.join(args.train, "train.csv")
    test_file = os.path.join(args.test, "test.csv")

    print(f"Reading training data from: {train_file}")
    tr = pd.read_csv(train_file)
    print(f"Reading test data from: {test_file}")
    te = pd.read_csv(test_file)

    # Separate features and target
    # Note: 'target' is 0 for malignant, 1 for benign
    X_tr, y_tr = tr.drop("target", axis=1), tr["target"]
    X_te, y_te = te.drop("target", axis=1), te["target"]

    print(f"Training features shape: {X_tr.shape}, Test features shape: {X_te.shape}")

    # Train Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=42
    )
    model.fit(X_tr, y_tr)

    # Generate predictions
    pred = model.predict(X_te)
    prob = model.predict_proba(X_te)[:, 1]

    # Metrics formatted for SageMaker Regex capture
    acc = accuracy_score(y_te, pred)
    prec = precision_score(y_te, pred)
    rec = recall_score(y_te, pred)
    f1 = f1_score(y_te, pred)
    auc = roc_auc_score(y_te, prob)

    print(f"test_accuracy={acc:.4f}")
    print(f"test_precision={prec:.4f}")
    print(f"test_recall={rec:.4f}")
    print(f"test_f1={f1:.4f}")
    print(f"test_auc={auc:.4f}")

    # Confusion matrix output
    cm = confusion_matrix(y_te, pred)
    print("\nConfusion Matrix [TN, FP / FN, TP]:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_te, pred, target_names=["Malignant (0)", "Benign (1)"]))

    # Save trained model artifact to model_dir
    os.makedirs(args.model_dir, exist_ok=True)
    model_save_path = os.path.join(args.model_dir, "model.joblib")
    joblib.dump(model, model_save_path)
    print(f"Model saved successfully to {model_save_path}")

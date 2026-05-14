import mlflow

# ── Connexion à la base SQLite ────────────────────────────
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("insider_threat_detection")

runs = [
    {
        "name": "Isolation_Forest",
        "params": {
            "model": "IsolationForest",
            "contamination": "0.05",
            "n_estimators": "100",
            "max_samples": "auto",
            "quantile": "q90",
            "threshold": "0.5682",
            "dataset": "internal_13users",
        },
        "metrics": {
            "precision": 1.000, "recall": 0.385,
            "f1": 0.556, "auc_roc": 0.923, "auc_pr": 0.049,
        }
    },
    {
        "name": "Autoencoder",
        "params": {
            "model": "Autoencoder",
            "architecture": "29-16-8-16-29",
            "epochs_total": "914",
            "best_epoch": "884",
            "quantile": "q98",
            "threshold": "1.3018",
            "dataset": "internal_13users",
        },
        "metrics": {
            "precision": 1.000, "recall": 1.000,
            "f1": 1.000, "auc_roc": 0.921, "auc_pr": 0.204,
            "train_loss": 0.1926, "val_loss": 0.0564,
        }
    },
    {
        "name": "LSTM_AE",
        "params": {
            "model": "LSTM_Autoencoder",
            "architecture": "LSTM(32)+latent(8)",
            "sequence_len": "7",
            "epochs_total": "189",
            "best_epoch": "159",
            "quantile": "q92",
            "threshold": "1.6656",
            "dataset": "internal_13users",
        },
        "metrics": {
            "precision": 0.409, "recall": 0.409,
            "f1": 0.409, "auc_roc": 0.734, "auc_pr": 0.039,
            "train_loss": 0.4373, "val_loss": 0.5868,
        }
    },
    {
        "name": "DBSCAN",
        "params": {
            "model": "DBSCAN",
            "epsilon": "0.1021",
            "k_neighbors": "5",
            "n_features": "7",
            "quantile": "q99",
            "threshold": "0.5219",
            "dataset": "internal_13users",
        },
        "metrics": {
            "precision": 0.576, "recall": 0.704,
            "f1": 0.633, "auc_roc": 0.846, "auc_pr": 0.087,
            "n_clusters": 43,
        }
    },
    {
        "name": "Consensus_4models",
        "params": {
            "model": "Consensus",
            "n_models": "4",
            "consensus_threshold": "1",
            "dataset": "internal_13users",
        },
        "metrics": {
            "recall_burst": 1.0, "recall_night": 1.0,
            "recall_long_session": 1.0, "recall_global": 1.0,
            "windows_detected": 27, "windows_total": 27,
            "auc_roc": 0.959, "auc_pr": 0.168,
        }
    },
    {
        "name": "Consensus_CERT_r4.2",
        "params": {
            "model": "Consensus",
            "dataset": "CERT_r4.2_1000users",
            "n_users": "1000",
            "insider": "AJR0932",
            "split": "DateOffset_7months",
        },
        "metrics": {
            "insider_detected": 1,
            "consensus_insider": 4,
            "recall_global": 1.0,
        }
    },
]

for run in runs:
    with mlflow.start_run(run_name=run["name"]):
        for k, v in run["params"].items():
            mlflow.log_param(k, v)
        for k, v in run["metrics"].items():
            mlflow.log_metric(k, v)
    print(f"✅ {run['name']} loggé")

print("\n✅ Tous les runs loggés — actualise http://localhost:5000")
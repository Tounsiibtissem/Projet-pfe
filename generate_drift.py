import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    ColumnDistributionMetric,
)

# ── Chargement données ────────────────────────────────────
df = pd.read_csv("pfe_scores_fenetres.csv", parse_dates=["Date"])

MID = "2026-08-12"
reference = df[df["Date"] <  MID][["score_IF","score_AE","score_LSTM","score_DBSCAN"]].reset_index(drop=True)
current   = df[df["Date"] >= MID][["score_IF","score_AE","score_LSTM","score_DBSCAN"]].reset_index(drop=True)

print(f"Référence : {len(reference)} fenêtres (mai → août 2026)")
print(f"Courant   : {len(current)}   fenêtres (août → nov 2026)")

# ── Rapport 1 : Data Drift complet ───────────────────────
report_drift = Report(metrics=[
    DatasetDriftMetric(),
    DataDriftPreset(),
    ColumnDriftMetric(column_name="score_IF"),
    ColumnDriftMetric(column_name="score_AE"),
    ColumnDriftMetric(column_name="score_LSTM"),
    ColumnDriftMetric(column_name="score_DBSCAN"),
    ColumnDistributionMetric(column_name="score_IF"),
    ColumnDistributionMetric(column_name="score_AE"),
    ColumnDistributionMetric(column_name="score_LSTM"),
    ColumnDistributionMetric(column_name="score_DBSCAN"),
])

report_drift.run(reference_data=reference, current_data=current)
report_drift.save_html("drift_report.html")
print("✅ drift_report.html généré")

# ── Rapport 2 : Data Quality ─────────────────────────────
report_quality = Report(metrics=[DataQualityPreset()])
report_quality.run(reference_data=reference, current_data=current)
report_quality.save_html("quality_report.html")
print("✅ quality_report.html généré")

# ── Résumé console ───────────────────────────────────────
result = report_drift.as_dict()
drift_detected = result["metrics"][0]["result"]["dataset_drift"]
n_drifted      = result["metrics"][0]["result"]["number_of_drifted_columns"]
n_total        = result["metrics"][0]["result"]["number_of_columns"]
share_drifted  = result["metrics"][0]["result"]["share_of_drifted_columns"]

print("\n" + "="*50)
print("RÉSUMÉ DATA DRIFT")
print("="*50)
print(f"Drift détecté      : {'OUI ⚠️' if drift_detected else 'NON ✅'}")
print(f"Features driftées  : {n_drifted}/{n_total}")
print(f"Share drift        : {share_drifted:.1%}")

# Détail par feature
for col in ["score_IF", "score_AE", "score_LSTM", "score_DBSCAN"]:
    for m in result["metrics"]:
        if m.get("metric") == "ColumnDriftMetric":
            if m["result"].get("column_name") == col:
                d = m["result"]["drift_detected"]
                s = m["result"]["drift_score"]
                print(f"  {col:15} : {'DRIFT ⚠️' if d else 'Stable ✅'} (score={s:.4f})")
print("="*50)
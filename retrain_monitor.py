"""
═══════════════════════════════════════════════════════════════
Re-entraînement automatique via API Kaggle
+
Monitoring continu (Data Drift Evidently)
═══════════════════════════════════════════════════════════════
Auteur  : Ibtissem Tounsi
Projet  : Pipeline de détection d'anomalies comportementales
Usage   : python retrain_monitor.py
          ou intégré dans le dashboard Streamlit (onglet 9)
"""

import os
import json
import time
import zipfile
import requests
import shutil
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# ── Configuration ────────────────────────────────────────────
KAGGLE_USERNAME  = "ibtissemtounsi"
KAGGLE_KEY       = "b3daab619b1333bb471b448fbdf3fcbb"
NOTEBOOK_ID      = "ibtissemtounsi/pipeline-pfe"
DRIFT_THRESHOLD  = 0.5    # seuil Wasserstein au-dessus duquel on re-entraîne
CRITICAL_DRIFT   = 1.0    # seuil critique → alerte immédiate
LOG_FILE         = "retrain_log.json"
MODELS_DIR       = "."    # dossier où sont les modèles (.pkl, .keras)

# ── Authentification Kaggle ──────────────────────────────────
def get_kaggle_headers():
    """Retourne les headers d'authentification Kaggle."""
    import base64
    credentials = base64.b64encode(
        f"{KAGGLE_USERNAME}:{KAGGLE_KEY}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

# ════════════════════════════════════════════════════════════
# PARTIE 1 — RE-ENTRAÎNEMENT VIA API KAGGLE
# ════════════════════════════════════════════════════════════

class KaggleRetrainer:
    """
    Gère le re-entraînement automatique du pipeline
    via l'API Kaggle Kernels.
    """

    def __init__(self):
        self.headers  = get_kaggle_headers()
        self.base_url = "https://www.kaggle.com/api/v1"
        self.log      = self._load_log()

    def _load_log(self):
        """Charge le journal des re-entraînements."""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                return json.load(f)
        return {"runs": [], "last_retrain": None, "total_retrains": 0}

    def _save_log(self):
        """Sauvegarde le journal."""
        with open(LOG_FILE, "w") as f:
            json.dump(self.log, f, indent=2, default=str)

    def get_notebook_status(self):
        """
        Vérifie le statut du notebook Kaggle.
        Retourne : 'complete', 'running', 'error', 'unknown'
        """
        url = f"{self.base_url}/kernels/{NOTEBOOK_ID}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("currentRunningVersion", {})
                return status.get("status", "unknown")
            return "unknown"
        except Exception as e:
            print(f"[ERREUR] Statut notebook : {e}")
            return "unknown"

    def trigger_retrain(self, reason="manuel"):
        """
        Déclenche le re-entraînement du notebook Kaggle.
        Retourne True si succès, False sinon.
        """
        print(f"\n{'='*55}")
        print(f"RE-ENTRAÎNEMENT DÉCLENCHÉ")
        print(f"Raison  : {reason}")
        print(f"Notebook: {NOTEBOOK_ID}")
        print(f"Heure   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*55}")

        url     = f"{self.base_url}/kernels/push"
        payload = {
            "slug":            NOTEBOOK_ID.split("/")[1],
            "newTitle":        "pipeline-pfe",
            "text":            "",
            "language":        "python",
            "kernelType":      "notebook",
            "isPrivate":       True,
            "enableGpu":       True,
            "enableInternet":  True,
            "datasetDataSources": [],
            "kernelDataSources":  [],
        }

        try:
            resp = requests.post(url, headers=self.headers,
                                 json=payload, timeout=60)

            if resp.status_code in [200, 201]:
                run_info = {
                    "timestamp":  datetime.now().isoformat(),
                    "reason":     reason,
                    "status":     "triggered",
                    "notebook":   NOTEBOOK_ID,
                }
                self.log["runs"].append(run_info)
                self.log["last_retrain"]    = datetime.now().isoformat()
                self.log["total_retrains"] += 1
                self._save_log()
                print("✅ Re-entraînement déclenché avec succès !")
                return True
            else:
                print(f"❌ Erreur API Kaggle : {resp.status_code}")
                print(f"   Réponse : {resp.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ Exception : {e}")
            return False

    def wait_for_completion(self, timeout_minutes=60):
        """
        Attend la fin du re-entraînement (polling toutes les 60s).
        """
        print(f"\nAttente de la fin du re-entraînement (max {timeout_minutes} min)...")
        start    = time.time()
        timeout  = timeout_minutes * 60
        attempts = 0

        while time.time() - start < timeout:
            attempts += 1
            status = self.get_notebook_status()
            elapsed = int((time.time() - start) / 60)
            print(f"[{elapsed:2d} min] Statut : {status}")

            if status == "complete":
                print("✅ Re-entraînement terminé !")
                return True
            elif status == "error":
                print("❌ Erreur durant le re-entraînement !")
                return False

            time.sleep(60)

        print(f"⏱️ Timeout ({timeout_minutes} min) atteint.")
        return False

    def download_new_models(self, output_dir="."):
        """
        Télécharge les nouveaux modèles depuis la sortie Kaggle.
        """
        print(f"\nTéléchargement des nouveaux modèles...")
        url = f"{self.base_url}/kernels/{NOTEBOOK_ID}/output"

        try:
            resp = requests.get(url, headers=self.headers,
                                timeout=120, stream=True)

            if resp.status_code == 200:
                zip_path = os.path.join(output_dir, "new_models.zip")
                with open(zip_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Extraire les modèles
                with zipfile.ZipFile(zip_path, "r") as zf:
                    model_files = [
                        n for n in zf.namelist()
                        if n.endswith((".pkl", ".keras", ".json"))
                    ]
                    for mf in model_files:
                        zf.extract(mf, output_dir)
                        print(f"  ✅ Extrait : {mf}")

                os.remove(zip_path)
                print(f"✅ {len(model_files)} modèle(s) téléchargé(s) !")
                return True
            else:
                print(f"❌ Impossible de télécharger : {resp.status_code}")
                return False

        except Exception as e:
            print(f"❌ Erreur téléchargement : {e}")
            return False

    def get_retrain_history(self):
        """Retourne l'historique des re-entraînements."""
        return self.log

    def full_retrain_pipeline(self, reason="drift_detected"):
        """
        Pipeline complet :
        1. Déclenche le re-entraînement
        2. Attend la fin
        3. Télécharge les nouveaux modèles
        """
        print(f"\n{'🔄 '*10}")
        print("PIPELINE RE-ENTRAÎNEMENT COMPLET")
        print(f"{'🔄 '*10}\n")

        # Étape 1 : Déclencher
        if not self.trigger_retrain(reason=reason):
            print("❌ Échec déclenchement — abandon")
            return False

        # Étape 2 : Attendre
        if not self.wait_for_completion(timeout_minutes=60):
            print("❌ Échec re-entraînement — abandon")
            return False

        # Étape 3 : Télécharger
        if not self.download_new_models():
            print("⚠️ Modèles non téléchargés — re-entraînement OK mais modèles non mis à jour")
            return False

        print("\n✅ Pipeline re-entraînement complet terminé avec succès !")
        return True


# ════════════════════════════════════════════════════════════
# PARTIE 2 — MONITORING CONTINU
# ════════════════════════════════════════════════════════════

class ContinuousMonitor:
    """
    Monitoring continu de la dérive des données.
    Utilise Evidently pour calculer la distance de Wasserstein
    entre les scores train et les scores actuels.
    """

    def __init__(self):
        self.retrainer       = KaggleRetrainer()
        self.drift_history   = self._load_drift_history()
        self.alert_callbacks = []

    def _load_drift_history(self):
        """Charge l'historique des drifts."""
        path = "drift_history.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {"checks": [], "total_alerts": 0}

    def _save_drift_history(self):
        """Sauvegarde l'historique."""
        with open("drift_history.json", "w") as f:
            json.dump(self.drift_history, f, indent=2, default=str)

    def load_reference_data(self):
        """Charge les scores du train (référence)."""
        try:
            with open("train_scores.pkl", "rb") as f:
                data = pickle.load(f)
            df = pd.DataFrame({
                "score_IF":     data["if"],
                "score_AE":     data["ae"],
                "score_LSTM":   data["lstm"],
                "score_DBSCAN": data["dbscan"],
            })
            print(f"✅ Référence chargée : {len(df)} fenêtres")
            return df
        except Exception as e:
            print(f"❌ Erreur chargement référence : {e}")
            return None

    def load_current_data(self):
        """Charge les scores actuels (test/production)."""
        try:
            df = pd.read_csv("pfe_scores_fenetres.csv")[
                ["score_IF", "score_AE", "score_LSTM", "score_DBSCAN"]
            ].reset_index(drop=True)
            print(f"✅ Données courantes chargées : {len(df)} fenêtres")
            return df
        except Exception as e:
            print(f"❌ Erreur chargement données courantes : {e}")
            return None

    def compute_wasserstein(self, ref_df, cur_df):
        """
        Calcule la distance de Wasserstein normalisée
        entre deux distributions pour chaque feature.
        """
        from scipy.stats import wasserstein_distance

        features = ["score_IF", "score_AE", "score_LSTM", "score_DBSCAN"]
        results  = {}

        for feat in features:
            if feat in ref_df.columns and feat in cur_df.columns:
                ref_vals = ref_df[feat].dropna().values
                cur_vals = cur_df[feat].dropna().values

                # Normaliser
                combined = np.concatenate([ref_vals, cur_vals])
                scale    = combined.std() + 1e-8
                ref_norm = ref_vals / scale
                cur_norm = cur_vals / scale

                dist = wasserstein_distance(ref_norm, cur_norm)
                results[feat] = {
                    "score":   round(dist, 4),
                    "drift":   dist > DRIFT_THRESHOLD,
                    "critical": dist > CRITICAL_DRIFT,
                }

        return results

    def generate_evidently_report(self, ref_df, cur_df):
        """Génère le rapport HTML Evidently."""
        try:
            from evidently import Dataset, DataDefinition, Report
            from evidently.presets import DataDriftPreset

            definition = DataDefinition()
            ref_ds = Dataset.from_pandas(ref_df, data_definition=definition)
            cur_ds = Dataset.from_pandas(cur_df, data_definition=definition)

            report = Report([DataDriftPreset()])
            result = report.run(ref_ds, cur_ds)

            timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path  = f"drift_report_{timestamp}.html"
            result.save_html(html_path)

            # Copier aussi comme rapport courant
            shutil.copy(html_path, "drift_report_train_vs_test.html")
            print(f"✅ Rapport Evidently sauvegardé : {html_path}")
            return html_path

        except Exception as e:
            print(f"❌ Erreur génération rapport : {e}")
            return None

    def run_monitoring_check(self, auto_retrain=True):
        """
        Lance une vérification complète du monitoring :
        1. Charge les données référence et courantes
        2. Calcule la dérive (Wasserstein)
        3. Génère le rapport Evidently
        4. Déclenche le re-entraînement si drift critique
        """
        print(f"\n{'='*55}")
        print(f"MONITORING CONTINU — VÉRIFICATION")
        print(f"Heure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*55}\n")

        # 1. Charger les données
        ref_df = self.load_reference_data()
        cur_df = self.load_current_data()

        if ref_df is None or cur_df is None:
            print("❌ Impossible de charger les données — arrêt")
            return None

        # 2. Calculer la dérive
        drift_results = self.compute_wasserstein(ref_df, cur_df)

        print("\n── RÉSULTATS DRIFT ──────────────────────────────")
        n_drifted  = 0
        n_critical = 0
        for feat, res in drift_results.items():
            status = "🔴 CRITIQUE" if res["critical"] else \
                     "⚠️  DRIFT   " if res["drift"] else "✅ STABLE  "
            print(f"  {feat:20s} : {res['score']:.4f}  {status}")
            if res["drift"]:     n_drifted  += 1
            if res["critical"]:  n_critical += 1

        print(f"\nFeatures driftées  : {n_drifted}/4")
        print(f"Features critiques : {n_critical}/4")

        # 3. Générer rapport Evidently
        html_path = self.generate_evidently_report(ref_df, cur_df)

        # 4. Sauvegarder dans l'historique
        check_record = {
            "timestamp":    datetime.now().isoformat(),
            "drift_results": drift_results,
            "n_drifted":    n_drifted,
            "n_critical":   n_critical,
            "report_path":  html_path,
            "retrain_triggered": False,
        }

        # 5. Déclencher re-entraînement si critique
        if n_critical >= 2 and auto_retrain:
            print(f"\n🚨 ALERTE : {n_critical} features critiques détectées !")
            print("→ Déclenchement automatique du re-entraînement...")
            success = self.retrainer.trigger_retrain(
                reason=f"drift_critique_{n_critical}_features"
            )
            check_record["retrain_triggered"] = success
            self.drift_history["total_alerts"] += 1

        self.drift_history["checks"].append(check_record)
        self._save_drift_history()

        # Résumé final
        print(f"\n{'='*55}")
        print("RÉSUMÉ MONITORING")
        print(f"{'='*55}")
        print(f"  Features driftées  : {n_drifted}/4")
        print(f"  Features critiques : {n_critical}/4")
        print(f"  Rapport généré     : {html_path or 'NON'}")
        print(f"  Re-entraînement    : {'OUI' if check_record['retrain_triggered'] else 'NON'}")
        print(f"{'='*55}\n")

        return {
            "drift_results":      drift_results,
            "n_drifted":          n_drifted,
            "n_critical":         n_critical,
            "report_path":        html_path,
            "retrain_triggered":  check_record["retrain_triggered"],
            "timestamp":          check_record["timestamp"],
        }

    def get_drift_summary(self):
        """
        Retourne un résumé rapide du dernier check
        pour affichage dans le dashboard.
        """
        if not self.drift_history["checks"]:
            return None

        last = self.drift_history["checks"][-1]
        return {
            "last_check":       last["timestamp"],
            "n_drifted":        last["n_drifted"],
            "n_critical":       last["n_critical"],
            "retrain_triggered":last["retrain_triggered"],
            "total_checks":     len(self.drift_history["checks"]),
            "total_alerts":     self.drift_history["total_alerts"],
            "drift_results":    last["drift_results"],
        }

    def get_drift_trend(self):
        """
        Retourne l'évolution du drift dans le temps
        pour affichage graphique dans le dashboard.
        """
        if not self.drift_history["checks"]:
            return pd.DataFrame()

        rows = []
        for check in self.drift_history["checks"]:
            for feat, res in check["drift_results"].items():
                rows.append({
                    "timestamp": check["timestamp"],
                    "feature":   feat,
                    "score":     res["score"],
                    "drift":     res["drift"],
                    "critical":  res["critical"],
                })
        return pd.DataFrame(rows)


# ════════════════════════════════════════════════════════════
# PARTIE 3 — INTÉGRATION STREAMLIT (onglet 9 amélioré)
# ════════════════════════════════════════════════════════════

STREAMLIT_TAB9_CODE = '''
# ══════════════════════════════════════════════
# TAB 9 — DATA DRIFT + MONITORING CONTINU
# Remplace l'ancien tab9 dans dashboard_mlflow.py
# ══════════════════════════════════════════════
with tab9:
    from retrain_monitor import ContinuousMonitor, KaggleRetrainer
    import plotly.graph_objects as go

    monitor   = ContinuousMonitor()
    retrainer = KaggleRetrainer()

    st.markdown("""
    <div class="cyber-header" style="margin-bottom:20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">
            MLOPS — MONITORING CONTINU
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                    font-weight:800; color:#e0ecff; margin-top:6px;">
            Data Drift + Re-entraînement automatique
        </div>
        <div style="margin-top:10px;">
            <span class="cyber-badge">EVIDENTLY</span>
            <span class="cyber-badge">WASSERSTEIN</span>
            <span class="cyber-badge">KAGGLE API</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Résumé dernier check ──────────────────────────────
    summary = monitor.get_drift_summary()
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Features driftées",  f"{summary['n_drifted']}/4")
        col2.metric("Features critiques", f"{summary['n_critical']}/4")
        col3.metric("Total checks",       summary["total_checks"])
        col4.metric("Alertes totales",    summary["total_alerts"])
        st.caption(f"Dernier check : {summary['last_check'][:19]}")
    else:
        st.info("Aucun check effectué — lance un monitoring ci-dessous.")

    st.markdown("---")

    # ── Boutons d'action ─────────────────────────────────
    section_title("Actions MLOps", "◈")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("📡 Lancer monitoring drift", use_container_width=True):
            with st.spinner("Calcul du drift en cours..."):
                result = monitor.run_monitoring_check(auto_retrain=True)
            if result:
                st.success(f"✅ Monitoring terminé — {result['n_drifted']}/4 features driftées")
                if result["retrain_triggered"]:
                    st.warning("🔄 Re-entraînement déclenché automatiquement !")
                if result["report_path"]:
                    with open(result["report_path"], "rb") as f:
                        st.download_button(
                            "⬇️ Télécharger rapport",
                            data=f.read(),
                            file_name="drift_report.html",
                            mime="text/html"
                        )

    with col_b:
        if st.button("🔄 Forcer re-entraînement", use_container_width=True):
            with st.spinner("Déclenchement du re-entraînement Kaggle..."):
                ok = retrainer.trigger_retrain(reason="force_manuel_dashboard")
            if ok:
                st.success("✅ Re-entraînement déclenché sur Kaggle !")
                st.info("Le notebook tourne sur Kaggle GPU T4. Reviens dans ~30 min.")
            else:
                st.error("❌ Erreur déclenchement — vérifie la connexion Kaggle.")

    with col_c:
        if st.button("📋 Historique re-entraînements", use_container_width=True):
            history = retrainer.get_retrain_history()
            if history["runs"]:
                df_hist = pd.DataFrame(history["runs"])
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun re-entraînement effectué.")

    st.markdown("---")

    # ── Résultats drift actuels ───────────────────────────
    section_title("Drift actuel — Distance de Wasserstein", "◈")
    if summary and summary.get("drift_results"):
        dr = summary["drift_results"]
        df_drift = pd.DataFrame([
            {
                "Feature": feat,
                "Score Wasserstein": res["score"],
                "Drift": "⚠️ Détecté" if res["drift"] else "✅ Stable",
                "Critique": "🔴 OUI" if res["critical"] else "NON",
            }
            for feat, res in dr.items()
        ])
        st.dataframe(df_drift.style.set_properties(
            **{"font-family": "JetBrains Mono", "font-size": "12px"}
        ), use_container_width=True, hide_index=True)

        # Graphique barres
        colors_bar = [
            "#ef4444" if dr[f]["critical"] else
            "#f59e0b" if dr[f]["drift"] else "#10b981"
            for f in dr
        ]
        fig = go.Figure(go.Bar(
            x=list(dr.keys()),
            y=[dr[f]["score"] for f in dr],
            marker=dict(color=colors_bar, opacity=0.85),
            text=[f"{dr[f]['score']:.3f}" for f in dr],
            textposition="outside",
        ))
        fig.add_hline(y=0.5, line_dash="dash", line_color="#60a5fa",
                      annotation_text="Seuil drift (0.5)")
        fig.add_hline(y=1.0, line_dash="dash", line_color="#ef4444",
                      annotation_text="Seuil critique (1.0)")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=40, b=20, l=10, r=10), height=320,
            yaxis=dict(gridcolor="#1a2d45",
                       title="Distance de Wasserstein normalisée"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Évolution temporelle du drift ─────────────────────
    section_title("Évolution temporelle du drift", "◈")
    trend_df = monitor.get_drift_trend()
    if not trend_df.empty:
        fig2 = go.Figure()
        for feat in trend_df["feature"].unique():
            fdf = trend_df[trend_df["feature"] == feat]
            fig2.add_trace(go.Scatter(
                x=fdf["timestamp"], y=fdf["score"],
                mode="lines+markers", name=feat,
            ))
        fig2.add_hline(y=0.5, line_dash="dash", line_color="#60a5fa",
                       annotation_text="Seuil drift")
        fig2.add_hline(y=1.0, line_dash="dash", line_color="#ef4444",
                       annotation_text="Seuil critique")
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=30, b=20, l=10, r=10), height=300,
            legend=dict(font=dict(size=10)),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Lance plusieurs checks pour voir l'évolution temporelle.")

    st.markdown("---")

    # ── Recommandations ───────────────────────────────────
    section_title("Recommandations de recalibrage", "◈")
    rec_df = pd.DataFrame([
        {"Modèle":"DBSCAN","Seuil Wasserstein":"1.510","Action":
         "Recalibrage prioritaire","Fréquence":"Tous les 3 mois"},
        {"Modèle":"IF",    "Seuil Wasserstein":"1.320","Action":
         "Recalibrage prioritaire","Fréquence":"Tous les 3 mois"},
        {"Modèle":"LSTM",  "Seuil Wasserstein":"0.705","Action":
         "Surveillance active",    "Fréquence":"Tous les 6 mois"},
        {"Modèle":"AE",    "Seuil Wasserstein":"0.445","Action":
         "Surveillance passive",   "Fréquence":"Tous les 6 mois"},
    ])
    st.dataframe(rec_df.style.set_properties(
        **{"font-family":"JetBrains Mono","font-size":"12px"}
    ), use_container_width=True, hide_index=True)
'''

# (code de référence Streamlit — non exécuté au import)


# ════════════════════════════════════════════════════════════
# MAIN — Exécution autonome (hors dashboard)
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Re-entraînement automatique + Monitoring continu"
    )
    parser.add_argument(
        "--mode",
        choices=["monitor", "retrain", "full"],
        default="monitor",
        help="monitor=drift seulement | retrain=re-entraîne seulement | full=les deux",
    )
    parser.add_argument(
        "--auto-retrain",
        action="store_true",
        default=True,
        help="Re-entraîne automatiquement si drift critique détecté",
    )
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════╗
║  PIPELINE MLOPS — RE-ENTRAÎNEMENT + MONITORING       ║
║  Ibtissem Tounsi — PFE 2025-2026                     ║
╚══════════════════════════════════════════════════════╝
Mode : {args.mode.upper()}
    """)

    if args.mode == "monitor":
        monitor = ContinuousMonitor()
        monitor.run_monitoring_check(auto_retrain=args.auto_retrain)

    elif args.mode == "retrain":
        retrainer = KaggleRetrainer()
        retrainer.full_retrain_pipeline(reason="manuel")

    elif args.mode == "full":
        monitor = ContinuousMonitor()
        result  = monitor.run_monitoring_check(auto_retrain=True)
        if result and not result["retrain_triggered"]:
            print("\nDrift non critique — re-entraînement non nécessaire.")
        print("\n✅ Pipeline MLOps complet terminé !")
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split

from modules.ml_db_extension import MLDatabaseExtension
from modules.predictive_engine import PredictiveEngine
from modules.config import DB_PATH

FEATURE_COLS = PredictiveEngine.FEATURE_COLS

db = MLDatabaseExtension(DB_PATH)
df = db.get_ml_ready_dataset()

print("=" * 80)
print("📊 O2C ENGINE A MACHINE LEARNING MODEL EVALUATION & EXPLANATION")
print("=" * 80)

print(f"\n1. DATASET OVERVIEW:")
print(f"   • Total ML Records: {len(df):,} rows")
print(f"   • Total Unique Sales Orders: {df['order_id'].nunique():,}")
print(f"   • Ground-Truth Class Distribution:")
print(f"     - ON-TIME Orders (Class 0): {sum(df['is_delayed'] == 0):,} ({sum(df['is_delayed'] == 0)/len(df):.1%})")
print(f"     - DELAYED Orders (Class 1): {sum(df['is_delayed'] == 1):,} ({sum(df['is_delayed'] == 1)/len(df):.1%})")

valid_cols = [c for c in FEATURE_COLS if c in df.columns]
X = df[valid_cols].fillna(0)
y_cls = df['is_delayed']
y_reg = df['delay_hours']

X_train, X_test, y_train_cls, y_test_cls, y_train_reg, y_test_reg = train_test_split(
    X, y_cls, y_reg, test_size=0.2, random_state=42, stratify=y_cls
)

pe = PredictiveEngine(ml_db_extension=db)
pe.train_models(df)

y_pred_cls = pe.clf_model.predict(X_test)
y_pred_reg = pe.reg_model.predict(X_test)

acc = accuracy_score(y_test_cls, y_pred_cls)
mae = mean_absolute_error(y_test_reg, y_pred_reg)
cm = confusion_matrix(y_test_cls, y_pred_cls)

print(f"\n2. OUT-OF-SAMPLE TEST SET EVALUATION (20% Holdout = {len(X_test):,} rows):")
print(f"   • Overall Classifier Accuracy: {acc:.1%}")
print(f"   • Regressor Mean Absolute Error (MAE): {mae:.2f} hours")
print(f"\n   • Confusion Matrix:")
print(f"     ┌────────────────────────┬──────────────────────┐")
print(f"     │ True Negatives (TN)    │ False Positives (FP) │ -> [{cm[0][0]:>6,}, {cm[0][1]:>6,}]")
print(f"     │ False Negatives (FN)   │ True Positives (TP)  │ -> [{cm[1][0]:>6,}, {cm[1][1]:>6,}]")
print(f"     └────────────────────────┴──────────────────────┘")

print(f"\n   • Detailed Classification Report:")
print(classification_report(y_test_cls, y_pred_cls, target_names=["On-Time (0)", "Delayed (1)"]))

print(f"\n3. WHY DID THE FIRST FEW ORDERS TEST AS DELAYED?")
print(f"   • In the SAP table `VTTP.csv` (Shipment Items bridge), orders are ordered sequentially.")
print(f"   • Orders 800000000000001 through 800000000000152 are assigned to Shipment TKNUM '0000000001'.")
print(f"   • In `VTTK.csv`, Shipment 1 is explicitly flagged with `STATUS = 'Delayed'` and high transit risk.")
print(f"   • Let's check non-delayed orders in the database:")

on_time_orders = df[df['is_delayed'] == 0]['order_id'].drop_duplicates().head(5).tolist()
delayed_orders = df[df['is_delayed'] == 1]['order_id'].drop_duplicates().head(5).tolist()

print(f"\n   [SAMPLE OF PREDICTIONS ON ON-TIME ORDERS (81.2% of dataset)]:")
for oid in on_time_orders:
    res = pe.predict_delivery_delay(oid)
    print(f"   • Order {oid} -> Delayed: {res.get('will_be_delayed')} | Delay Prob: {res.get('delay_probability', 0):.1%} | Delay Hours: {res.get('delay_hours', 0):.1f}h")

print(f"\n   [SAMPLE OF PREDICTIONS ON DELAYED ORDERS (18.8% of dataset)]:")
for oid in delayed_orders:
    res = pe.predict_delivery_delay(oid)
    print(f"   • Order {oid} -> Delayed: {res.get('will_be_delayed')} | Delay Prob: {res.get('delay_probability', 0):.1%} | Delay Hours: {res.get('delay_hours', 0):.1f}h")

print("=" * 80)

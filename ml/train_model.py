import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
import joblib
import warnings

warnings.filterwarnings("ignore")

try:
    from imblearn.over_sampling import SMOTE

    SMOTE_AVAILABLE = True
    print("SMOTE available")
except:
    SMOTE_AVAILABLE = False
    print("SMOTE not available - skipping balancing")

DATA_PATH = "D:/medisimplify/ml/data"
SAVE_PATH = "D:/medisimplify/ml"

print("=" * 60)
print("MediSimplify - Multi-Model Comparison Pipeline")
print("=" * 60)

MODELS = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000, random_state=42, solver="lbfgs"
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=6, random_state=42, n_jobs=-1
    ),
    "XGBoost": XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
        use_label_encoder=False,
    ),
    "SVM": SVC(kernel="rbf", C=1.0, probability=True, random_state=42),
    "KNN": KNeighborsClassifier(n_neighbors=7, metric="euclidean"),
}

# ============================================================
# STEP 1 - LOAD RAW DATA
# ============================================================


def load_raw_data():
    print("\nSTEP 1: Loading raw datasets...")
    datasets = {}

    try:
        df = pd.read_csv(f"{DATA_PATH}/diabetes.csv")
        datasets["diabetes"] = {"df": df, "target_col": "Outcome"}
        print(f"  Diabetes: {df.shape[0]} rows, target=Outcome")
    except Exception as e:
        print(f"  Diabetes error: {e}")

    try:
        df = pd.read_csv(f"{DATA_PATH}/heart-selected-columns.csv")
        df = df.replace("?", np.nan)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        datasets["heart"] = {"df": df, "target_col": "target"}
        print(f"  Heart: {df.shape[0]} rows, target=target")
        print(f"  Heart columns: {list(df.columns)}")
    except Exception as e:
        print(f"  Heart error: {e}")
  
    try:
        df = pd.read_csv(f"{DATA_PATH}/kidney_disease.csv")
        df = df.apply(
            lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x)
        )
        # Remove id — not a medical feature, causes leakage
        df = df.drop(columns=['id'], errors='ignore')
        datasets["kidney"] = {"df": df, "target_col": "classification"}
        print(f"  Kidney: {df.shape[0]} rows, target=classification")
    except Exception as e:
        print(f"  Kidney error: {e}")

    return datasets


# ============================================================
# STEP 2 - CREATE RISK LABELS
# Must happen BEFORE feature engineering to prevent leakage
# ============================================================


def create_risk_labels(df, name, target_col):
    print(f"\nSTEP 2: Creating risk labels for {name}...")

    if name == "diabetes":

        def risk(row):
            if row["Outcome"] == 1:
                if row["Glucose"] > 140 or row["BMI"] > 35:
                    return 2  # High
                return 1  # Medium
            else:
                if row["Glucose"] > 100:
                    return 1  # Medium prediabetic
                return 0  # Low

        df["risk"] = df.apply(risk, axis=1)

    elif name == "heart":
        print(f"  Unique target values: {df[target_col].unique()}")
        df[target_col] = pd.to_numeric(df[target_col], errors="coerce").fillna(0)

        def risk(row):
            val = int(row[target_col])
            if val == 0:
                return 0  # No disease = Low
            elif val == 1:
                if "thalach" in df.columns:
                    if row.get("thalach", 150) < 120:
                        return 2  # High
                return 1  # Medium
            else:
                return 2  # Values 2,3,4 = High

        df["risk"] = df.apply(risk, axis=1)

    elif name == "kidney":
        print(f"  Unique target values: {df[target_col].unique()}")

        def risk(row):
            val = str(row[target_col]).strip().lower()
            if val in ["ckd", "ckd\t", "1"]:
                try:
                    sc_val = float(row.get("sc", 1.2))
                except:
                    sc_val = 1.2
                try:
                    hemo_val = float(row.get("hemo", 13.0))
                except:
                    hemo_val = 13.0
                try:
                    bp_val = float(row.get("bp", 80.0))
                except:
                    bp_val = 80.0

                # High: severe indicators
                if sc_val > 2.0 or hemo_val < 10.0 or bp_val > 100:
                    return 2  # High
                # Medium: mild kidney damage
                return 1  # Medium
            return 0  # Low

        df["risk"] = df.apply(risk, axis=1)

    # Drop original target to prevent leakage
    df = df.drop(columns=[target_col], errors="ignore")

    counts = df["risk"].value_counts().sort_index()
    labels = {0: "Low", 1: "Medium", 2: "High"}
    for level, count in counts.items():
        print(f"  {labels.get(level, level)} Risk: {count} samples")

    return df


# ============================================================
# STEP 3 - HANDLE MISSING VALUES
# ============================================================


def handle_missing_values(df, name):
    print(f"\nSTEP 3: Handling missing values for {name}...")
    before = df.isnull().sum().sum()

    if name == "diabetes":
        zero_not_allowed = [
            "Glucose",
            "BloodPressure",
            "SkinThickness",
            "Insulin",
            "BMI",
        ]
        for col in zero_not_allowed:
            if col in df.columns:
                df[col] = df[col].replace(0, np.nan)

    # Convert all non-risk object columns to numeric
    for col in df.columns:
        if col != "risk" and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill numeric columns with median
    for col in df.select_dtypes(include=[np.number]).columns:
        if col != "risk":
            median_val = df[col].median()
            if pd.isna(median_val):
                median_val = 0
            df[col] = df[col].fillna(median_val)

    # Fill remaining object columns with mode
    for col in df.select_dtypes(include=["object"]).columns:
        if col != "risk":
            if len(df[col].mode()) > 0:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna("unknown")

    after = df.isnull().sum().sum()
    print(f"  Missing values: {before} -> {after}")
    return df


# ============================================================
# STEP 4 - REMOVE OUTLIERS
# ============================================================


def remove_outliers(df, name):
    print(f"\nSTEP 4: Removing outliers for {name}...")
    before = len(df)

    skip_cols = ["risk"]
    feature_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns if c not in skip_cols
    ]

    for col in feature_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3 * IQR
        upper = Q3 + 3 * IQR
        df = df[(df[col] >= lower) & (df[col] <= upper)]

    after = len(df)
    print(f"  Removed {before - after} rows -> {after} remaining")
    return df


# ============================================================
# STEP 5 - FEATURE ENGINEERING
# Done AFTER target removed — no leakage possible
# ============================================================


def engineer_features(df, name):
    print(f"\nSTEP 5: Feature engineering for {name}...")
    before_cols = len(df.columns)

    if name == "diabetes":
        df["bmi_category"] = pd.cut(
            df["BMI"], bins=[0, 18.5, 24.9, 29.9, 100], labels=[0, 1, 2, 3]
        ).astype(float)
        df["glucose_category"] = pd.cut(
            df["Glucose"], bins=[0, 99, 125, 500], labels=[0, 1, 2]
        ).astype(float)
        df["age_group"] = pd.cut(
            df["Age"], bins=[0, 30, 45, 60, 100], labels=[0, 1, 2, 3]
        ).astype(float)
        df["insulin_glucose_ratio"] = df["Insulin"] / (df["Glucose"] + 1)
        df["bmi_age_risk"] = df["BMI"] * df["Age"] / 100
        df["high_glucose_bmi"] = ((df["Glucose"] > 140) & (df["BMI"] > 30)).astype(int)

    elif name == "heart":
        if "age" in df.columns:
            df["age_group"] = pd.cut(
                df["age"], bins=[0, 40, 55, 65, 100], labels=[0, 1, 2, 3]
            ).astype(float)
        if "thalach" in df.columns:
            df["hr_category"] = pd.cut(
                df["thalach"], bins=[0, 100, 140, 170, 300], labels=[0, 1, 2, 3]
            ).astype(float)
            if "age" in df.columns:
                df["age_hr_risk"] = df["age"] / (df["thalach"] + 1) * 100
        if "cp" in df.columns:
            df["chest_pain_severe"] = (df["cp"] >= 3).astype(int)
        if "oldpeak" in df.columns:
            df["st_depression_risk"] = pd.cut(
                df["oldpeak"], bins=[-1, 1, 2, 10], labels=[0, 1, 2]
            ).astype(float)
        if "thalach" in df.columns and "age" in df.columns:
            df["max_hr_reserve"] = 220 - df["age"] - df["thalach"]
        if "chol" in df.columns:
            df["chol_category"] = pd.cut(
                df["chol"], bins=[0, 200, 240, 600], labels=[0, 1, 2]
            ).astype(float)

    elif name == "kidney":
        if "sc" in df.columns:
            df["gfr_stage"] = pd.cut(
                df["sc"], bins=[0, 1.2, 2.0, 3.5, 6.0, 100], labels=[0, 1, 2, 3, 4]
            ).astype(float)
        if "hemo" in df.columns:
            df["anemia_flag"] = (df["hemo"] < 12).astype(int)
        if "bp" in df.columns:
            df["bp_category"] = pd.cut(
                df["bp"], bins=[0, 80, 90, 120, 300], labels=[0, 1, 2, 3]
            ).astype(float)
        if "bgr" in df.columns:
            df["high_blood_glucose"] = (df["bgr"] > 140).astype(int)
        if "bu" in df.columns:
            df["high_urea"] = (df["bu"] > 40).astype(int)
        risk_cols = [
            c
            for c in ["anemia_flag", "gfr_stage", "high_blood_glucose", "high_urea"]
            if c in df.columns
        ]
        if risk_cols:
            df["combined_risk_score"] = df[risk_cols].sum(axis=1)

    added = len(df.columns) - before_cols
    print(f"  New features added: {added}")
    return df


# ============================================================
# STEP 6 - ENCODE CATEGORIES
# ============================================================


def encode_categories(df):
    print(f"\nSTEP 6: Encoding categorical variables...")
    encoded = 0
    for col in df.select_dtypes(include=["object"]).columns:
        if col != "risk":
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoded += 1
    print(f"  Encoded {encoded} categorical columns")
    return df


# ============================================================
# STEP 7 + 8 - SCALE AND SELECT FEATURES
# ============================================================


def scale_and_select(X_train, X_test, y_train, feature_names):
    print(f"\nSTEP 7: Scaling features...")
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    print(f"\nSTEP 8: Selecting best features...")
    k = min(15, X_train_s.shape[1])
    selector = SelectKBest(score_func=f_classif, k=k)
    X_train_f = selector.fit_transform(X_train_s, y_train)
    X_test_f = selector.transform(X_test_s)

    selected = [feature_names[i] for i, s in enumerate(selector.get_support()) if s]
    print(f"  Selected top {k} features from {len(feature_names)}")
    print(f"  Top features: {selected[:5]}")
    return X_train_f, X_test_f, scaler, selector, selected


# ============================================================
# STEP 9 - COMPARE ALL MODELS + OVERFITTING CHECK
# ============================================================


def compare_models(X_train, y_train, X_test, y_test, name):
    print(f"\nSTEP 9: Comparing models on {name}...")

    actual_classes = sorted(y_test.unique())
    label_map = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
    target_names = [label_map[c] for c in actual_classes]

    print("-" * 65)
    print(
        f"  {'Model':<25} {'Test Acc':>9} {'CV Score':>9} "
        f"{'AUC':>7} {'Overfit?':>9}"
    )
    print("-" * 65)

    results = {}

    for model_name, model in MODELS.items():
        try:
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            test_acc = (y_pred == y_test).mean()

            y_train_pred = model.predict(X_train)
            train_acc = (y_train_pred == y_train).mean()

            cv_scores = cross_val_score(
                model, X_train, y_train, cv=5, scoring="accuracy"
            )
            cv_mean = cv_scores.mean()

            try:
                y_prob = model.predict_proba(X_test)
                if len(actual_classes) == 2:
                    auc = roc_auc_score(y_test, y_prob[:, 1])
                else:
                    auc = roc_auc_score(
                        y_test, y_prob, multi_class="ovr", average="weighted"
                    )
            except:
                auc = 0.0

            gap = train_acc - cv_mean
            overfit = "YES" if gap > 0.10 else "No"

            results[model_name] = {
                "model": model,
                "test_acc": test_acc,
                "train_acc": train_acc,
                "cv_score": cv_mean,
                "auc": auc,
                "overfit": overfit,
                "gap": gap,
            }

            print(
                f"  {model_name:<25} {test_acc:>8.2%} "
                f"{cv_mean:>8.2%} {auc:>6.3f} {overfit:>9}"
            )

        except Exception as e:
            print(f"  {model_name:<25} Error: {e}")

    print("-" * 65)

    if not results:
        raise ValueError("No models trained successfully")

    non_overfit = {k: v for k, v in results.items() if v["overfit"] == "No"}

    if non_overfit:
        best_name = max(non_overfit, key=lambda x: non_overfit[x]["cv_score"])
    else:
        print("  All models overfit — picking lowest gap")
        best_name = min(results, key=lambda x: results[x]["gap"])

    best = results[best_name]

    print(f"\n  WINNER: {best_name}")
    print(f"  Test Accuracy  : {best['test_acc']:.2%}")
    print(f"  Train Accuracy : {best['train_acc']:.2%}")
    print(f"  CV Score       : {best['cv_score']:.2%}")
    print(f"  AUC            : {best['auc']:.3f}")
    print(f"  Overfit Gap    : {best['gap']:.2%}")

    best["model"].fit(X_train, y_train)
    y_pred = best["model"].predict(X_test)
    print(f"\n  Detailed report for {best_name}:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=actual_classes,
            target_names=target_names,
            zero_division=0,
        )
    )

    return best_name, best, results


# ============================================================
# MAIN PIPELINE
# ============================================================


def run_pipeline():
    raw_datasets = load_raw_data()
    all_models = {}
    summary = {}

    for name, data in raw_datasets.items():
        df = data["df"].copy()
        target_col = data["target_col"]

        print(f"\n{'='*60}")
        print(f"  DATASET: {name.upper()}")
        print(f"{'='*60}")

        try:
            # Correct order — labels first, then features
            df = create_risk_labels(df, name, target_col)
            df = handle_missing_values(df, name)
            df = remove_outliers(df, name)
            df = engineer_features(df, name)
            df = encode_categories(df)

            X = df.drop(columns=["risk"]).select_dtypes(include=[np.number])
            y = df["risk"]

            if len(y.unique()) < 2:
                print(f"  Skipping: only 1 class found")
                continue

            print(f"\n  Final shape: {X.shape[0]} samples, " f"{X.shape[1]} features")
            print(f"  Classes: {sorted(y.unique())}")
            counts = y.value_counts().sort_index()
            for cls, cnt in counts.items():
                lbl = {0: "Low", 1: "Medium", 2: "High"}.get(cls, cls)
                print(f"  {lbl}: {cnt} samples")

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            X_train_f, X_test_f, scaler, selector, selected = scale_and_select(
                X_train, X_test, y_train, X.columns.tolist()
            )

            # Apply SMOTE to fix class imbalance
            if SMOTE_AVAILABLE:
                class_counts = pd.Series(y_train).value_counts()
                min_count = class_counts.min()
                max_count = class_counts.max()
                imbalance_ratio = max_count / min_count

                if min_count >= 2 and imbalance_ratio > 1.5:
                    try:
                        # Limit synthetic samples to 3x minority
                        # Prevents overfitting from too many fake samples
                        max_samples = min(min_count * 3, max_count)
                        sampling_strategy = {
                            cls: max_samples
                            for cls, cnt in class_counts.items()
                            if cnt < max_samples
                        }

                        k_neighbors = min(5, min_count - 1)
                        smote = SMOTE(
                            random_state=42,
                            k_neighbors=k_neighbors,
                            sampling_strategy=sampling_strategy,
                        )
                        X_train_f, y_train = smote.fit_resample(X_train_f, y_train)
                        print(f"\n  After SMOTE: {len(y_train)} samples")
                        new_counts = pd.Series(y_train).value_counts().sort_index()
                        for cls, cnt in new_counts.items():
                            lbl = {0: "Low", 1: "Medium", 2: "High"}.get(cls, cls)
                            print(f"    {lbl}: {cnt}")
                    except Exception as e:
                        print(f"  SMOTE skipped: {e}")
                else:
                    print(f"  SMOTE skipped: ratio {imbalance_ratio:.1f} ok")

            best_name, best_data, all_results = compare_models(
                X_train_f, y_train, X_test_f, y_test, name
            )

            all_models[name] = {
                "model": best_data["model"],
                "model_name": best_name,
                "scaler": scaler,
                "selector": selector,
                "features": X.columns.tolist(),
                "selected_features": selected,
                "test_accuracy": best_data["test_acc"],
                "cv_score": best_data["cv_score"],
                "auc": best_data["auc"],
                "overfit": best_data["overfit"],
            }

            summary[name] = {
                "best_model": best_name,
                "test_acc": best_data["test_acc"],
                "cv_score": best_data["cv_score"],
                "overfit": best_data["overfit"],
            }

        except Exception as e:
            print(f"  Error: {e}")
            import traceback

            traceback.print_exc()

    if all_models:
        save_path = f"{SAVE_PATH}/risk_models.pkl"
        joblib.dump(all_models, save_path)

        print(f"\n{'='*60}")
        print("  FINAL SUMMARY")
        print(f"{'='*60}")
        print(
            f"  {'Dataset':<12} {'Best Model':<25} "
            f"{'Test Acc':>9} {'CV Score':>9} {'Overfit':>8}"
        )
        print(f"  {'-'*63}")
        for n, d in summary.items():
            print(
                f"  {n:<12} {d['best_model']:<25} "
                f"{d['test_acc']:>8.2%} "
                f"{d['cv_score']:>8.2%} "
                f"{d['overfit']:>8}"
            )
        print(f"\n  Models saved to: {save_path}")
    else:
        print("\n  No models trained successfully")


if __name__ == "__main__":
    run_pipeline()

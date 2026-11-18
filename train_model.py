
# import sqlite3
# from pathlib import Path
# import json

# import pandas as pd
# import joblib

# from sklearn.compose import ColumnTransformer
# from sklearn.preprocessing import OneHotEncoder
# from sklearn.impute import SimpleImputer
# from sklearn.pipeline import Pipeline
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import GroupShuffleSplit
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# BASE_DIR = Path(__file__).resolve().parent

# PROJECT_DIR = BASE_DIR.parent

# DATA_PATH = PROJECT_DIR / "dataset" / "travelmate_pakistan_tourist_places.csv"
# DB_PATH = PROJECT_DIR / "sqlite database" / "feedback.db"
# MODEL_DIR = PROJECT_DIR / "models"
# MODEL_DIR.mkdir(exist_ok=True)


# def main():

#     if not DB_PATH.exists():
#         print("Feedback database not found. Run the Streamlit app first.")
#         return

#     places = pd.read_csv(DATA_PATH)

#     with sqlite3.connect(DB_PATH) as conn:
#         feedback = pd.read_sql_query(
#             "SELECT place_name, rating FROM feedback",
#             conn
#         )

#     if len(feedback) < 20:
#         print(
#             f"Only {len(feedback)} feedback records found. "
#             "Collect at least 20 real feedback records first."
#         )
#         return

#     # Merge actual user ratings with place information
#     data = feedback.merge(
#         places,
#         on="place_name",
#         how="inner"
#     )

#     if len(data) < 20:
#         print("Not enough feedback matched with the tourist dataset.")
#         return

#     if data["rating_x"].nunique() < 2:
#         print("Feedback ratings need variation (for example 2, 3, 4, 5).")
#         return

#     data = data.rename(columns={"rating_x": "user_rating"})

#     feature_columns = [
#         "city",
#         "category",
#         "description",
#         "interests",
#         "entry_fee",
#         "rating_y"
#     ]

#     # In the dataset, rating_y is the original place rating
#     X = data[feature_columns].copy()
#     y = pd.to_numeric(data["user_rating"], errors="coerce")

#     X["entry_fee"] = pd.to_numeric(
#         X["entry_fee"], errors="coerce"
#     )
#     X["rating_y"] = pd.to_numeric(
#         X["rating_y"], errors="coerce"
#     )

#     valid = y.notna()
#     X = X.loc[valid].copy()
#     y = y.loc[valid].copy()
#     groups = data.loc[valid, "place_name"]

#     if groups.nunique() < 5:
#         print(
#             "Collect feedback for at least 5 different places "
#             "before training and testing this model."
#         )
#         return

#     # Keep places separate between train and test sets
#     splitter = GroupShuffleSplit(
#         n_splits=1,
#         test_size=0.20,
#         random_state=42
#     )

#     train_idx, test_idx = next(
#         splitter.split(X, y, groups=groups)
#     )

#     X_train = X.iloc[train_idx]
#     X_test = X.iloc[test_idx]
#     y_train = y.iloc[train_idx]
#     y_test = y.iloc[test_idx]

#     categorical_features = [
#         "city", "category", "description", "interests"
#     ]
#     numerical_features = ["entry_fee", "rating_y"]

#     preprocessor = ColumnTransformer(
#         transformers=[
#             (
#                 "categorical",
#                 Pipeline([
#                     ("imputer", SimpleImputer(
#                         strategy="constant", fill_value="Unknown"
#                     )),
#                     ("onehot", OneHotEncoder(
#                         handle_unknown="ignore"
#                     ))
#                 ]),
#                 categorical_features
#             ),
#             (
#                 "numerical",
#                 Pipeline([
#                     ("imputer", SimpleImputer(strategy="median"))
#                 ]),
#                 numerical_features
#             )
#         ]
#     )

#     model = Pipeline([
#         ("preprocessor", preprocessor),
#         ("regressor", RandomForestRegressor(
#             n_estimators=200,
#             random_state=42,
#             min_samples_leaf=2
#         ))
#     ])

#     model.fit(X_train, y_train)

#     predictions = model.predict(X_test)

#     mae = mean_absolute_error(y_test, predictions)
#     rmse = mean_squared_error(y_test, predictions) ** 0.5

#     r2 = (
#         r2_score(y_test, predictions)
#         if len(y_test) >= 2 and y_test.nunique() >= 2
#         else None
#     )

#     model_path = MODEL_DIR / "random_forest_model.pkl"
#     joblib.dump(model, model_path)

#     metrics = {
#         "feedback_records": int(len(data)),
#         "different_places": int(groups.nunique()),
#         "train_records": int(len(X_train)),
#         "test_records": int(len(X_test)),
#         "MAE": float(mae),
#         "RMSE": float(rmse),
#         "R2": float(r2) if r2 is not None else None
#     }

#     with open(MODEL_DIR / "evaluation_metrics.json", "w") as file:
#         json.dump(metrics, file, indent=4)

#     print("\nRandom Forest training completed.")
#     print(f"Model saved at: {model_path}")
#     print("\nEvaluation:")
#     for name, value in metrics.items():
#         print(f"{name}: {value}")


# if __name__ == "__main__":
#     main()

import sqlite3
import json
from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score
)


# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DATA_PATH = (
    PROJECT_DIR / "dataset"
    / "travelmate_pakistan_tourist_places.csv"
)

DB_PATH = (
    PROJECT_DIR / "sqlite database"
    / "feedback.db"
)

MODEL_DIR = PROJECT_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)


# =====================================================
# MAIN FUNCTION
# =====================================================

def main():

    print("\n======================================")
    print(" TRAVELMATE PAKISTAN MODEL EVALUATION")
    print("======================================")

    if not DATA_PATH.exists():
        print("Dataset file not found:", DATA_PATH)
        return

    if not DB_PATH.exists():
        print("Feedback database not found:", DB_PATH)
        return

    # Load dataset
    places = pd.read_csv(DATA_PATH)

    places = places.dropna(
        subset=["place_name"]
    ).copy()

    # Load feedback
    with sqlite3.connect(DB_PATH) as conn:

        feedback = pd.read_sql_query(
            "SELECT place_name, rating FROM feedback",
            conn
        )

    feedback["rating"] = pd.to_numeric(
        feedback["rating"],
        errors="coerce"
    )

    feedback = feedback.dropna(
        subset=["place_name", "rating"]
    ).copy()

    if len(feedback) < 10:
        print("Not enough feedback records.")
        return

    # =================================================
    # MERGE DATA
    # =================================================

    data = feedback.merge(
        places,
        on="place_name",
        how="inner",
        suffixes=("_user", "_place")
    )

    if data.empty:
        print("No matching feedback records found.")
        return

    y = pd.to_numeric(
        data["rating_user"],
        errors="coerce"
    )

    feature_columns = [
        "city",
        "category",
        "description",
        "interests",
        "entry_fee",
        "rating_place"
    ]

    X = data[feature_columns].copy()

    X = X.rename(
        columns={"rating_place": "rating_y"}
    )

    X["entry_fee"] = pd.to_numeric(
        X["entry_fee"],
        errors="coerce"
    )

    X["rating_y"] = pd.to_numeric(
        X["rating_y"],
        errors="coerce"
    )

    valid = y.notna()

    X = X.loc[valid].reset_index(drop=True)
    y = y.loc[valid].reset_index(drop=True)

    groups = (
        data.loc[valid, "place_name"]
        .reset_index(drop=True)
    )

    if groups.nunique() < 5:
        print("Feedback is needed for at least 5 different places.")
        return

    # =================================================
    # TRAIN TEST SPLIT
    # =================================================

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42
    )

    train_idx, test_idx = next(
        splitter.split(X, y, groups=groups)
    )

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    if len(y_test) < 2:
        print("Test records are insufficient.")
        return

    # =================================================
    # PREPROCESSING
    # =================================================

    categorical_features = [
        "city",
        "category",
        "description",
        "interests"
    ]

    numerical_features = [
        "entry_fee",
        "rating_y"
    ]

    preprocessor = ColumnTransformer(
        transformers=[

            (
                "categorical",

                Pipeline([
                    (
                        "imputer",
                        SimpleImputer(
                            strategy="constant",
                            fill_value="Unknown"
                        )
                    ),

                    (
                        "onehot",
                        OneHotEncoder(
                            handle_unknown="ignore"
                        )
                    )
                ]),

                categorical_features
            ),

            (
                "numerical",

                Pipeline([
                    (
                        "imputer",
                        SimpleImputer(
                            strategy="median"
                        )
                    )
                ]),

                numerical_features
            )
        ]
    )

    # =================================================
    # RANDOM FOREST MODEL
    # =================================================

    model = Pipeline([

        ("preprocessor", preprocessor),

        (
            "regressor",

            RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                min_samples_leaf=2
            )
        )
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # =================================================
    # RANDOM FOREST EVALUATION
    # =================================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = (
        r2_score(y_test, predictions)
        if y_test.nunique() >= 2
        else None
    )

    # =================================================
    # BASELINE COMPARISON
    # =================================================

    baseline_predictions = [
        y_train.mean()
    ] * len(y_test)

    baseline_mae = mean_absolute_error(
        y_test,
        baseline_predictions
    )

    baseline_rmse = mean_squared_error(
        y_test,
        baseline_predictions
    ) ** 0.5

    baseline_r2 = (
        r2_score(y_test, baseline_predictions)
        if y_test.nunique() >= 2
        else None
    )

    # =================================================
    # STAR RATING ACCURACY
    # =================================================

    actual_stars = (
        y_test.round()
        .clip(1, 5)
        .astype(int)
    )

    predicted_stars = (
        pd.Series(predictions, index=y_test.index)
        .round()
        .clip(1, 5)
        .astype(int)
    )

    exact_accuracy = accuracy_score(
        actual_stars,
        predicted_stars
    )

    within_one_accuracy = (
        (actual_stars - predicted_stars).abs() <= 1
    ).mean()

    # Baseline accuracy
    baseline_stars = pd.Series(
        baseline_predictions,
        index=y_test.index
    ).round().clip(1, 5).astype(int)

    baseline_accuracy = accuracy_score(
        actual_stars,
        baseline_stars
    )

    baseline_within_one = (
        (actual_stars - baseline_stars).abs() <= 1
    ).mean()

    # =================================================
    # SAVE MODEL
    # =================================================

    model_path = (
        MODEL_DIR / "random_forest_model.pkl"
    )

    joblib.dump(model, model_path)

    # =================================================
    # SAVE TEST PREDICTIONS
    # =================================================

    prediction_table = pd.DataFrame({

        "place_name": groups.iloc[test_idx].values,

        "actual_rating": y_test.values,

        "predicted_rating": predictions,

        "actual_stars": actual_stars.values,

        "predicted_stars": predicted_stars.values,

        "absolute_error": abs(
            y_test.values - predictions
        )
    })

    prediction_table.to_csv(
        MODEL_DIR / "test_predictions.csv",
        index=False
    )

    # =================================================
    # SAVE EVALUATION METRICS
    # =================================================

    metrics = {

        "feedback_records": int(len(data)),

        "different_places": int(groups.nunique()),

        "training_records": int(len(X_train)),

        "testing_records": int(len(X_test)),

        "Random_Forest": {

            "MAE": round(float(mae), 4),

            "RMSE": round(float(rmse), 4),

            "R2": (
                round(float(r2), 4)
                if r2 is not None
                else None
            ),

            "Exact_Star_Accuracy_Percent": round(
                float(exact_accuracy * 100), 2
            ),

            "Within_One_Star_Accuracy_Percent": round(
                float(within_one_accuracy * 100), 2
            )
        },

        "Mean_Rating_Baseline": {

            "MAE": round(float(baseline_mae), 4),

            "RMSE": round(float(baseline_rmse), 4),

            "R2": (
                round(float(baseline_r2), 4)
                if baseline_r2 is not None
                else None
            ),

            "Exact_Star_Accuracy_Percent": round(
                float(baseline_accuracy * 100), 2
            ),

            "Within_One_Star_Accuracy_Percent": round(
                float(baseline_within_one * 100), 2
            )
        },

        "Evaluation_Note": (
            "Star accuracy measures rounded user-rating prediction. "
            "It is not the accuracy of the complete recommendation ranking."
        )
    }

    with open(
        MODEL_DIR / "evaluation_metrics.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    # =================================================
    # ACTUAL VS PREDICTED GRAPH
    # =================================================

    plt.figure(figsize=(7, 6))

    plt.scatter(
        y_test,
        predictions
    )

    plt.plot(
        [1, 5],
        [1, 5],
        linestyle="--"
    )

    plt.xlabel("Actual User Rating")
    plt.ylabel("Predicted User Rating")

    plt.title(
        "TravelMate - Actual vs Predicted Ratings"
    )

    plt.xlim(1, 5)
    plt.ylim(1, 5)

    plt.tight_layout()

    plt.savefig(
        MODEL_DIR / "actual_vs_predicted.png",
        dpi=150
    )

    plt.close()

    # =================================================
    # PRINT FINAL RESULTS
    # =================================================

    print("\n========== RANDOM FOREST RESULTS ==========")

    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")

    print(
        f"R2: {r2:.4f}"
        if r2 is not None
        else "R2: Not available"
    )

    print(
        f"Exact Star Accuracy: {exact_accuracy * 100:.2f}%"
    )

    print(
        f"Within One Star Accuracy: {within_one_accuracy * 100:.2f}%"
    )

    print("\n========== BASELINE RESULTS ==========")

    print(f"Baseline MAE: {baseline_mae:.4f}")
    print(f"Baseline RMSE: {baseline_rmse:.4f}")

    print(
        f"Baseline Exact Accuracy: {baseline_accuracy * 100:.2f}%"
    )

    print(
        f"Baseline Within One Star: {baseline_within_one * 100:.2f}%"
    )

    print("\n========== SAVED FILES ==========")

    print("Model:", model_path)

    print(
        "Metrics:",
        MODEL_DIR / "evaluation_metrics.json"
    )

    print(
        "Predictions:",
        MODEL_DIR / "test_predictions.csv"
    )

    print(
        "Graph:",
        MODEL_DIR / "actual_vs_predicted.png"
    )

    print("\nEvaluation completed successfully.")

    print(
        "\nNote: These accuracy values evaluate rating prediction, "
        "not complete recommendation ranking."
    )


if __name__ == "__main__":
    main()
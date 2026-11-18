


import re
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# LOAD TRAINED RANDOM FOREST MODEL
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

MODEL_PATH = (
    PROJECT_DIR / "models" / "random_forest_model.pkl"
)

try:
    random_forest_model = joblib.load(MODEL_PATH)
    print("Random Forest model loaded successfully.")

except Exception as error:
    random_forest_model = None
    print(f"Random Forest model could not be loaded: {error}")


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).lower().strip()


# =========================================================
# RECOMMENDATION FUNCTION
# =========================================================

def recommend_places(
    df,
    budget,
    selected_interests,
    selected_city="All",
    minimum_rating=0,
    number_of_recommendations=5
):

    data = df.copy()

    data["entry_fee"] = pd.to_numeric(
        data["entry_fee"], errors="coerce"
    )

    data["rating"] = pd.to_numeric(
        data["rating"], errors="coerce"
    )

    # Budget and rating filters
    data = data[
        data["entry_fee"].notna()
        & (data["entry_fee"] <= budget)
        & data["rating"].notna()
        & (data["rating"] >= minimum_rating)
    ].copy()

    if selected_city != "All":
        data = data[
            data["city"].astype(str) == selected_city
        ].copy()

    if data.empty:
        return data

    # =====================================================
    # TF-IDF AND COSINE SIMILARITY
    # =====================================================

    text_columns = [
        "place_name",
        "category",
        "description",
        "interests"
    ]

    for col in text_columns:
        if col not in data.columns:
            data[col] = ""

    data["combined_text"] = data[text_columns].apply(
        lambda row: " ".join(
            clean_text(value) for value in row
        ),
        axis=1
    )

    if selected_interests:

        query = " ".join(selected_interests).lower()

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        try:
            place_matrix = vectorizer.fit_transform(
                data["combined_text"]
            )

            query_vector = vectorizer.transform([query])

            data["interest_score"] = cosine_similarity(
                query_vector,
                place_matrix
            ).flatten()

        except ValueError:
            data["interest_score"] = 0.0

    else:
        data["interest_score"] = 0.0

    # =====================================================
    # RANDOM FOREST PREDICTIONS
    # =====================================================

    data["predicted_rating"] = data["rating"]

    if random_forest_model is not None:

        try:
            rf_features = data[
                [
                    "city",
                    "category",
                    "description",
                    "interests",
                    "entry_fee",
                    "rating"
                ]
            ].copy()

            rf_features = rf_features.rename(
                columns={"rating": "rating_y"}
            )

            data["predicted_rating"] = (
                random_forest_model.predict(rf_features)
            )
            

        except Exception as error:
            print(
                "Random Forest prediction failed. "
                f"Using existing ratings instead: {error}"
            )

            data["predicted_rating"] = data["rating"]

    # =====================================================
    # HYBRID FINAL SCORE
    # =====================================================

    if random_forest_model is not None:

        if selected_interests:

            data["final_score"] = (
                0.60 * data["interest_score"]
                + 0.20 * (data["rating"] / 5)
                + 0.20 * (data["predicted_rating"] / 5)
            )

        else:

            data["final_score"] = (
                0.50 * (data["rating"] / 5)
                + 0.50 * (data["predicted_rating"] / 5)
            )

    else:

        # Fallback to the original recommendation formula
        if selected_interests:

            data["final_score"] = (
                0.70 * data["interest_score"]
                + 0.30 * (data["rating"] / 5)
            )

        else:
            data["final_score"] = data["rating"] / 5

    # =====================================================
    # SORT RECOMMENDATIONS
    # =====================================================

    data = data.sort_values(
        "final_score",
        ascending=False
    )

    return data.head(
        int(number_of_recommendations)
    )

from pathlib import Path
import sys
import re
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Expected layout: DatascienceProject/website/main.py
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "dataset" / "travelmate_pakistan_tourist_places.csv"
IMAGES_DIR = PROJECT_DIR / "images"

# Keep the existing project modules and their original folder names.
sys.path.insert(0, str(PROJECT_DIR / "recommender.py"))
sys.path.insert(0, str(PROJECT_DIR / "sqlite database"))
from recommender import recommend_places
from database import init_database, save_feedback, get_feedback_count, get_all_feedback

app = FastAPI(title="TravelMate Pakistan API", version="1.0.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

init_database()

def load_places():
    if not DATA_PATH.exists():
        raise RuntimeError(f"Dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = {"place_name", "city", "category", "description", "interests", "entry_fee", "latitude", "longitude", "rating"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError("Dataset missing columns: " + ", ".join(sorted(missing)))
    return df

DATA = load_places()

def clean(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())

def image_for(place_name):
    if not IMAGES_DIR.exists():
        return ""
    target = clean(place_name)
    candidates = sorted(p for p in IMAGES_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    exact = [p for p in candidates if clean(p.stem) == target]
    if exact:
        return "/images/" + exact[0].name
    partial = [p for p in candidates if target and (target in clean(p.stem) or clean(p.stem) in target)]
    if partial:
        return "/images/" + partial[0].name
    # Match on meaningful tokens for filenames that abbreviate the place name.
    tokens = [t for t in re.findall(r"[a-z0-9]+", str(place_name).lower()) if len(t) > 2]
    scored = [(sum(t in clean(p.stem) for t in tokens), p) for p in candidates]
    scored = [item for item in scored if item[0] > 0]
    if scored:
        scored.sort(key=lambda x: (-x[0], x[1].name))
        return "/images/" + scored[0][1].name
    return ""

def records(df):
    result = []
    for _, row in df.iterrows():
        item = {}
        for col in ["place_name", "city", "category", "description", "interests", "entry_fee", "latitude", "longitude", "rating"]:
            val = row.get(col, "")
            if pd.isna(val):
                val = ""
            if col in {"entry_fee", "latitude", "longitude", "rating"}:
                try: val = float(val)
                except (TypeError, ValueError): val = None
            item[col] = val
        item["image"] = image_for(item["place_name"])
        result.append(item)
    return result

class RecommendationRequest(BaseModel):
    budget: float = Field(default=500, ge=0, le=500)
    interests: list[str] = []
    city: str = "All"
    minimum_rating: float = Field(default=0, ge=0, le=5)
    number_of_recommendations: int = Field(default=6, ge=1, le=30)

class FeedbackRequest(BaseModel):
    place_name: str
    rating: int = Field(ge=1, le=5)
    review: str = ""

@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/explore")
def explore():
    return FileResponse(Path(__file__).parent / "static" / "explore.html")

@app.get("/about")
def about():
    return FileResponse(Path(__file__).parent / "static" / "about.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "project": "TravelMate Pakistan"}

@app.get("/api/filters")
def filters():
    return {
        "cities": ["All"] + sorted(DATA["city"].dropna().astype(str).unique().tolist()),
        "interests": sorted({x.strip() for value in DATA["interests"].dropna().astype(str) for x in re.split(r"[,;|]", value) if x.strip()}),
        "feedback_count": get_feedback_count()
    }

@app.get("/api/places")
def places():
    return records(DATA)

@app.post("/api/recommend")
def recommend(request: RecommendationRequest):
    try:
        selected = recommend_places(
            DATA.copy(),
            budget=request.budget,
            selected_interests=request.interests,
            selected_city=request.city,
            minimum_rating=request.minimum_rating,
            number_of_recommendations=request.number_of_recommendations
        )
        items = records(selected)
        return {"recommendations": items, "count": len(items)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {exc}")

@app.post("/api/feedback")
def feedback(request: FeedbackRequest):
    try:
        save_feedback(request.place_name.strip(), request.rating, request.review.strip())
        return {"message": "Feedback saved successfully.", "feedback_count": get_feedback_count()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not save feedback: {exc}")

@app.get("/api/feedback")
def feedback_list():
    rows = get_all_feedback()
    return {"feedback": [
        {"id": r[0], "place_name": r[1], "rating": r[2], "review": r[3], "created_at": r[4]}
        for r in rows
    ], "count": len(rows)}

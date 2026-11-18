import base64
import mimetypes
import os
import base64
from pathlib import Path

# Limit numerical library threads
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import streamlit as st
import pandas as pd
import re
import html
from pathlib import Path
import sys

# =========================================================
# PROJECT PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

IMAGE_DIR = BASE_DIR / "images"
HERO_IMAGE = IMAGE_DIR / "mountain_banner1.jpg"
DATA_PATH = BASE_DIR / "dataset" / "travelmate_pakistan_tourist_places.csv"

# Prepare mountain image for hero background
if HERO_IMAGE.exists():
    encoded_image = base64.b64encode(HERO_IMAGE.read_bytes()).decode("utf-8")
    hero_background = (
        "background: linear-gradient(90deg, rgba(6,27,44,.88), "
        "rgba(6,27,44,.42)), "
        f'url("data:image/jpeg;base64,{encoded_image}");'
        "background-size: cover; "
        "background-position: center; "
        "background-repeat: no-repeat;"
    )
else:
    hero_background = (
        "background: linear-gradient(105deg, "
        "rgba(8,126,139,.30), rgba(6,27,44,.94));"
    )

sys.path.insert(0, str(BASE_DIR / "recommender.py"))
sys.path.insert(0, str(BASE_DIR / "sqlite database"))

from database import init_database, save_feedback, get_feedback_count
from recommender import recommend_places

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="TravelMate Pakistan",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_database()

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

:root {
    --deep: #061B2C;
    --navy: #0B3448;
    --teal: #087E8B;
    --aqua: #12B8B0;
    --gold: #D5B779;
    --cream: #F4EBD5;
    --muted: #B9DCE0;
}

.stApp {
    background:
        radial-gradient(ellipse at 90% 0%, rgba(18,184,176,.17), transparent 34%),
        linear-gradient(135deg, #061B2C 0%, #0B3448 56%, #073D4B 100%);
    color: #F2F8F8;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

footer {
    visibility: hidden;
}

.block-container {
    max-width: 1240px;
    padding-top: 1.3rem;
    padding-bottom: 3rem;
}

/* BRAND BAR */

.brand-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 17px 22px;
    margin-bottom: 22px;
    border: 1px solid rgba(18,184,176,.35);
    border-radius: 16px;
    background: rgba(3,20,32,.75);
    box-shadow: 0 10px 30px rgba(0,0,0,.15);
}

.brand-name {
    color: var(--cream);
    font-size: 21px;
    font-weight: 800;
    letter-spacing: .7px;
}

.brand-name span {
    color: var(--gold);
}

.brand-note {
    color: var(--muted);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-align: right;
}

/* HERO */


.hero {
    position: relative;
    overflow: hidden;
    padding: 65px 45px;
    margin: 20px 0 30px;
    min-height: 360px;

    border: 1px solid rgba(213,183,121,.45);
    border-left: 5px solid var(--gold);
    border-radius: 8px 24px 8px 24px;

    background:
        linear-gradient(
            90deg,
            rgba(6, 27, 44, 0.88),
            rgba(6, 27, 44, 0.45)
        ),
        url("images/mountain_banner1.jpg");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: none;

    box-shadow: 0 20px 50px rgba(0,0,0,.22);
}

.hero h1 {
    color: #ffffff;
    font-size: 48px;
    font-weight: 800;
    margin-bottom: 18px;
}

.hero p {
    color: #ffffff;
    font-size: 17px;
    line-height: 1.8;
    max-width: 650px;
}

.hero-kicker {
    color: #D5B779;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 15px;
}



/* SECTION HEADINGS */

.eyebrow {
    color: var(--aqua);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2.5px;
    margin-bottom: 7px;
}

.section-heading {
    color: var(--cream);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 29px;
    font-weight: 700;
    margin: 0 0 6px 0;
}

.section-copy {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 18px;
}

/* INPUT LABELS */

.stSelectbox label,
.stTextArea label {
    color: var(--cream) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}

div[data-baseweb="select"] > div {
    background: #F4EBD5 !important;
    border: 1px solid rgba(18,184,176,.65) !important;
    border-radius: 10px !important;
    min-height: 45px;
}

div[data-baseweb="select"] * {
    color: #082B3D !important;
}

/* BUTTONS */

div.stButton > button,
div.stFormSubmitButton > button {
    width: 100%;
    min-height: 47px;
    border: 0;
    border-radius: 11px;
    color: #062536;
    background: linear-gradient(100deg, #12B8B0, #D5B779);
    font-weight: 800;
    letter-spacing: .5px;
    transition: .2s ease;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    color: #062536;
    background: #F4EBD5;
    transform: translateY(-2px);
}

/* STATISTICS */

.stat-card {
    padding: 19px 21px;
    margin: 4px 0 18px;
    border: 1px solid rgba(213,183,121,.42);
    border-radius: 15px;
    background: linear-gradient(135deg, rgba(18,184,176,.15), rgba(5,30,46,.8));
}

.stat-number {
    color: var(--gold);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 30px;
    font-weight: 800;
}

.stat-label {
    color: var(--muted);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.7px;
}

/* DESTINATION CARDS */

.place-card {
    padding: 20px;
    margin: 8px 0 18px;
    border: 1px solid rgba(91,208,208,.35);
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(5,30,46,.97), rgba(8,48,64,.96));
    box-shadow: 0 12px 30px rgba(0,0,0,.18);
}

.place-name {
    color: var(--gold);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 25px;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 12px;
}

.place-info {
    color: #D2E9E9;
    font-size: 13px;
    line-height: 1.9;
}

.score-box {
    padding: 12px;
    margin: 12px 0;
    border: 1px solid rgba(18,184,176,.24);
    border-radius: 11px;
    color: var(--cream);
    background: rgba(18,184,176,.10);
    font-size: 12px;
    line-height: 1.8;
}

.results-banner {
    padding: 17px 20px;
    border: 1px solid rgba(18,184,176,.35);
    border-radius: 14px;
    color: var(--cream);
    background: rgba(18,184,176,.10);
    margin: 12px 0 20px;
}

# /* INTEREST TAGS */

# .interest-tag {
#     display: inline-block;
#     background: #087E8B;
#     color: white;
#     padding: 7px 13px;
#     margin: 4px 4px 4px 0;
#     border-radius: 20px;
#     font-size: 12px;
#     font-weight: 600;
# }

/* FEEDBACK */

div[data-testid="stForm"] {
    padding: 16px;
    border: 1px solid rgba(91,208,208,.25);
    border-radius: 14px;
    background: rgba(3,20,32,.38);
}

div[data-testid="stDownloadButton"] button {
    width: 100%;
    border-radius: 11px;
    min-height: 46px;
    background: #D5B779;
    color: #062536;
    font-weight: 800;
    border: 0;
}

/* FOOTER */

.footer {
    margin-top: 42px;
    padding: 27px 18px;
    text-align: center;
    border-top: 1px solid rgba(91,208,208,.28);
}

.footer-title {
    color: var(--gold);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 21px;
    font-weight: 800;
}

.footer-copy {
    color: var(--muted);
    font-size: 12px;
    letter-spacing: .5px;
}

@media (max-width: 700px) {
    .block-container {
        padding: 1rem 1rem 2rem;
    }

    .brand-note {
        display: none;
    }

    .hero {
        padding: 30px 22px;
    }

    .hero h1 {
        font-size: 38px;
    }

    .section-heading {
        font-size: 25px;
    }
}
</style>
""".replace("HERO_BACKGROUND_PLACEHOLDER", hero_background), unsafe_allow_html=True)


# =========================================================
# LOAD DATASET
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

try:
    df = load_data()

except Exception as error:
    st.error(f"Dataset loading error: {error}")
    st.info(
        "Check karein ke CSV file dataset folder mein mojood hai."
    )
    st.stop()

required_columns = [
    "place_name",
    "city",
    "category",
    "description",
    "interests",
    "entry_fee",
    "latitude",
    "longitude",
    "rating"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Dataset mein columns missing hain: {missing_columns}")
    st.stop()


# =========================================================
# BRANDING AND HERO IMAGE
# =========================================================

HERO_IMAGE = IMAGE_DIR / "mountain_banner1.jpg"

# Load image as Base64
hero_background = ""

if HERO_IMAGE.exists():
    image_type = mimetypes.guess_type(str(HERO_IMAGE))[0] or "image/jpeg"
    encoded_image = base64.b64encode(HERO_IMAGE.read_bytes()).decode("utf-8")
    hero_background = f'url("data:{image_type};base64,{encoded_image}")'
else:
    st.warning("Mountain image nahi mili. images folder check karein.")

# Hero CSS
st.markdown(f"""
<style>
.hero {{
    min-height: 360px;
    padding: 65px 45px;
    margin: 20px 0 30px;
    border: 1px solid rgba(213,183,121,.45);
    border-left: 5px solid #D5B779;
    border-radius: 8px 24px 8px 24px;
    background-image:
        linear-gradient(90deg, rgba(6,27,44,.82), rgba(6,27,44,.35)),
        {hero_background if hero_background else "linear-gradient(135deg,#087E8B,#061B2C)"};
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    box-shadow: 0 20px 50px rgba(0,0,0,.22);
}}

.hero h1 {{
    color: white;
    font-size: 48px;
    font-weight: 800;
    margin: 15px 0;
}}

.hero p {{
    color: white;
    font-size: 17px;
    line-height: 1.8;
    max-width: 650px;
}}

.hero-kicker {{
    color: #D5B779;
    font-weight: bold;
    letter-spacing: 3px;
}}
</style>
""", unsafe_allow_html=True)

# Brand bar
st.markdown("""
<div class="brand-bar">
<div class="brand-name">
🌍 TRAVELMATE <span>PAKISTAN</span>
</div>
<div class="brand-note">
DISCOVER MORE · TRAVEL BETTER
</div>
</div>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero">
<div class="hero-kicker">YOUR NEXT STORY STARTS HERE</div>
<h1>Find your own<br>piece of Pakistan.</h1>
<p>From beautiful mountain valleys to timeless heritage, discover places that fit your interests, budget and travel style. Let TravelMate help you plan a journey worth remembering.</p>
</div>
""", unsafe_allow_html=True)




# =========================================================
# TRAVEL PREFERENCES
# =========================================================

st.markdown("""
<div class="eyebrow">MAKE IT PERSONAL</div>
<div class="section-heading">Plan your perfect journey</div>
<div class="section-copy">
Choose your preferences below to discover your next destination.
</div>
""", unsafe_allow_html=True)

# Extract interests individually from dataset
all_interests = sorted({
    item.strip().title()
    for value in df["interests"].dropna()
    for item in re.split(r"[,;]", str(value))
    if item.strip()
})

cities = ["All"] + sorted(
    df["city"].dropna().astype(str).unique().tolist()
)

budget_options = [
    0, 50, 100, 150, 200, 250,
    300, 350, 400, 450, 500
]

st.markdown("### 💚 Your travel preferences")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    budget = st.selectbox(
        "💰 Maximum budget (Rs.)",
        options=budget_options,
        index=5,
        format_func=lambda value: f"Rs. {value}"
    )

with filter_col2:
    selected_city = st.selectbox(
        "📍 Preferred city",
        options=cities,
        index=0
    )

with filter_col3:
    interest_options = ["All interests"] + all_interests

    selected_interest = st.selectbox(
        "💚 Travel interest",
        options=interest_options,
        index=0
    )

rating_col, count_col = st.columns(2)

with rating_col:
    minimum_rating = st.selectbox(
        "⭐ Minimum place rating",
        options=[0, 1, 2, 3, 3.5, 4, 4.5, 5],
        index=5,
        format_func=lambda value: f"{value} stars and above"
    )

with count_col:
    number_of_recommendations = st.selectbox(
        "🎯 Number of recommendations",
        options=[1, 2, 3, 4, 5, 6, 8, 10],
        index=4
    )

# Convert selected interest into recommender input format
selected_interests = (
    []
    if selected_interest == "All interests"
    else [selected_interest]
)

st.markdown("<br>", unsafe_allow_html=True)

search_clicked = st.button(
    "🌍 FIND MY PERFECT DESTINATIONS",
    use_container_width=True
)

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================

if search_clicked:

    try:
        results = recommend_places(
            df=df,
            budget=budget,
            selected_interests=selected_interests,
            selected_city=selected_city,
            minimum_rating=minimum_rating,
            number_of_recommendations=number_of_recommendations
        )

        st.session_state["travel_results"] = results
        st.session_state["travel_search_done"] = True

    except Exception as error:
        st.error(f"Recommendation error: {error}")

# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state.get("travel_search_done", False):

    results = st.session_state["travel_results"]

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="eyebrow">CURATED FOR YOU</div>
    <div class="section-heading">Your recommended destinations</div>
    <div class="section-copy">
        A collection selected around your travel preferences.
    </div>
    """, unsafe_allow_html=True)

    if results is None or results.empty:

        st.warning(
            "No destinations found. Please increase your budget "
            "or change your preferences."
        )

    else:

        stat_col1, stat_col2 = st.columns(2)

        with stat_col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(results):02d}</div>
                <div class="stat-label">DESTINATIONS FOUND</div>
            </div>
            """, unsafe_allow_html=True)

        with stat_col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">Rs. {budget}</div>
                <div class="stat-label">YOUR MAXIMUM BUDGET</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            f'<div class="results-banner">🌍 We found '
            f'<b>{len(results)}</b> destinations for you.</div>',
            unsafe_allow_html=True
        )


        for index, (_, place) in enumerate(
            results.iterrows(),
            start=1
        ):

            # Find destination image
            image_path = None

            if IMAGE_DIR.exists():

                target = re.sub(
                    r"[^a-z0-9]",
                    "",
                    str(place["place_name"]).lower()
                )

                for file in IMAGE_DIR.iterdir():

                    if file.suffix.lower() in [
                        ".jpg", ".jpeg", ".png", ".webp"
                    ]:

                        cleaned = re.sub(
                            r"[^a-z0-9]",
                            "",
                            file.stem.lower()
                        )

                        if cleaned == target:
                            image_path = file
                            break

            # Destination card
            st.markdown(
                f'<div class="place-card">'
                f'<div class="place-name">'
                f'{index:02d} / {html.escape(str(place["place_name"]))}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            image_col, info_col = st.columns([1, 1.7], gap="large")

            with image_col:
                if image_path is not None and image_path.exists():
                    st.image(
                        str(image_path),
                        use_container_width=True
                    )
                else:
                    st.write("Image not available")

            with info_col:
                st.markdown(
                    f'<div class="place-info">'
                    f'📍 &nbsp;{html.escape(str(place["city"]))}<br>'
                    f'🏷️ &nbsp;{html.escape(str(place["category"]))}<br>'
                    f'💰 &nbsp;Entry fee: Rs. {place["entry_fee"]}<br>'
                    f'⭐ &nbsp;Rating: {place["rating"]}/5'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="score-box">'
                    f'🎯 Interest match: '
                    f'{float(place["interest_score"]) * 100:.1f}%'
                    f'<br>🏆 Recommendation score: '
                    f'{float(place["final_score"]) * 100:.1f}%'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if pd.notna(place.get("description")):
                    st.write(place["description"])

            # =================================================
            # SHOW INTERESTS AS SEPARATE TAGS
            # =================================================
            # Separate dropdowns for multiple interests

            place_interests = [
                interest.strip().title()
                for interest in str(place["interests"]).split()
                if interest.strip()
            ]

            if place_interests:
                st.markdown("**💚 Select Your Interests:**")

                selected_interests = []

                

            # =================================================
            # FEEDBACK FORM
            # =================================================
            st.markdown("#### ⭐ Share your feedback")

            with st.form(key=f"feedback_form_{index}"):

                user_rating = st.selectbox(
                    "Your rating",
                    options=[1, 2, 3, 4, 5],
                    index=4,
                    format_func=lambda value: f"{value} / 5 stars",
                    key=f"rating_{index}"
                )

                user_review = st.text_area(
                    "Write your feedback",
                    key=f"review_{index}",
                    placeholder=(
                        "Please write your feedback here..."
                    )
                )

                submitted = st.form_submit_button(
                    "Submit feedback"
                )

                if submitted:

                    if not user_review.strip():

                        st.warning(
                            "⚠️ Please apna feedback jama karwayen "
                            "ya apni review mein changes karein."
                        )

                    else:

                        try:
                            save_feedback(
                                str(place["place_name"]),
                                user_rating,
                                user_review.strip()
                            )

                            st.success(
                                "✅ Thank you! Your feedback "
                                "has been successfully saved."
                            )

                        except Exception as error:
                            st.error(
                                f"Feedback save nahi hua: {error}"
                            )

       # Download recommendations
    csv_data = results.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
       "⬇️ Download your travel recommendations",
        data=csv_data,
        file_name="TravelMate_Recommendations.csv",
        mime="text/csv",
        key="travel_recommendations_download"
)
# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    <div class="footer-title">🌍 TravelMate Pakistan</div>
    <div class="footer-copy">
        DISCOVER THE BEAUTY OF PAKISTAN,
        ONE JOURNEY AT A TIME.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FEEDBACK SUMMARY
# =========================================================

with st.expander("📊 Feedback collection summary"):

    try:
        st.write(
            f"Total feedback records collected: {get_feedback_count()}"
        )

    except Exception as error:
        st.error(f"Could not load feedback summary: {error}")

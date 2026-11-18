# travelmate
# ✈️ TravelMate Pakistan
### AI-Powered Tourist Destination Recommendation System

TravelMate Pakistan is an intelligent tourism recommendation system designed to help users discover beautiful tourist destinations across Pakistan. The project uses Machine Learning to recommend places based on users' preferences, budget, city, interests, and ratings.

The main goal of TravelMate Pakistan is to make travel planning easier by helping tourists explore destinations that match their interests and travel requirements.

---

## 🌍 Project Overview

Pakistan is home to beautiful landscapes, historical landmarks, beaches, mountains, museums, and cultural attractions. However, tourists may find it difficult to choose destinations according to their preferences and budget.

TravelMate Pakistan addresses this problem through an AI-based recommendation system that suggests suitable tourist destinations.

The project provides two interfaces:

- **Streamlit Application:** An interactive interface for exploring destinations and receiving personalized recommendations.
- **FastAPI Website:** A web-based platform with Home, Explore, and About pages, connected to a recommendation backend.

---

## ✨ Key Features

### 1. AI-Based Destination Recommendations
- Recommends tourist destinations based on user preferences.
- Uses a trained Random Forest Machine Learning model.
- Supports personalized destination discovery.

### 2. Personalized Search Filters
Users can customize their recommendations using:
- Budget
- City
- Travel interests
- Minimum rating
- Number of recommendations

### 3. Destination Information
- Displays tourist destination cards.
- Includes destination photographs.
- Helps users explore different tourist attractions.

### 4. Machine Learning Techniques
The project incorporates:
- Random Forest Classifier
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Cosine Similarity

TF-IDF helps represent textual information numerically, while Cosine Similarity measures similarity between text-based destination descriptions and interests.

### 5. Feedback System
- Users can submit ratings and reviews.
- Feedback is stored in an SQLite database.
- Existing feedback can be retrieved for review.

### 6. Data Export
- Allows users to download recommendation results as CSV through the Streamlit application.

### 7. Web Interface
The FastAPI website includes:
- Home Page
- Explore Page
- About Page
- REST API endpoints
- Static HTML, CSS, and JavaScript frontend

---

## 🧠 Machine Learning Approach

TravelMate Pakistan uses machine learning techniques to support intelligent destination recommendations.

**Random Forest**

A Random Forest model is trained to learn patterns in the tourism dataset and support destination recommendation.

**TF-IDF**

TF-IDF converts textual information into numerical feature representations. It helps identify important terms in destination descriptions and travel interests.

**Cosine Similarity**

Cosine Similarity measures the similarity between text feature vectors. It can help identify destinations with descriptions that are relevant to users' selected interests.

**Model Evaluation**

The project includes model evaluation metrics saved in:

`models/evaluation_metrics.json`

The trained model is stored in:

`models/random_forest_model.pkl`

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive recommendation application |
| FastAPI | Backend API development |
| HTML | Website structure |
| CSS | Website styling |
| JavaScript | Frontend interactions |
| Pandas | Dataset handling |
| NumPy | Numerical operations |
| Scikit-learn | Machine Learning |
| TF-IDF | Text feature extraction |
| Cosine Similarity | Text similarity |
| Random Forest | Machine Learning model |
| SQLite | Feedback database |
| Uvicorn | FastAPI application server |

---

## 📁 Project Structure

```text
TravelMate-Pakistan/
│
├── app.py
│
├── dataset/
│   └── travelmate_pakistan_tourist_places.csv
│
├── images/
│   └── Destination Images
│
├── recommender.py/
│   └── recommender.py
│
├── sqlite database/
│   ├── database.py
│   └── feedback.db
│
├── train_model.py/
│   └── train_model.py
│
├── models/
│   ├── random_forest_model.pkl
│   └── evaluation_metrics.json
│
└── website/
    ├── main.py
    ├── requirements-website.txt
    ├── README_SETUP.txt
    │
    └── static/
        ├── index.html
        ├── explore.html
        ├── about.html
        ├── style.css
        └── app.js
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/TravelMate-Pakistan.git
```

### 2. Open the Project Directory

```bash
cd TravelMate-Pakistan
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

Install the dependencies required by your application:

```bash
pip install -r website/requirements-website.txt
```

If running the Streamlit application, make sure its required packages are also installed.

### 5. Run the Streamlit Application

```bash
streamlit run app.py
```

### 6. Run the FastAPI Website

From the project root directory:

```bash
uvicorn website.main:app --reload
```

Open the website:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

---

## 🔌 API Endpoints

The FastAPI backend provides the following endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Home page |
| `/explore` | GET | Explore page |
| `/about` | GET | About page |
| `/api/health` | GET | API health check |
| `/api/filters` | GET | Retrieve available filters |
| `/api/places` | GET | Retrieve tourist places |
| `/api/recommend` | POST | Generate recommendations |
| `/api/feedback` | POST | Submit user feedback |
| `/api/feedback` | GET | Retrieve feedback |

Interactive API documentation is available at `/docs`.

---

## 🗄️ Database

TravelMate Pakistan uses SQLite to store user feedback.

The feedback database stores:
- Place name
- User rating
- Review
- Feedback submission date and time

The database is initialized automatically by the backend.

---

## 📊 Dataset

The project uses a tourism dataset:

`travelmate_pakistan_tourist_places.csv`

The dataset contains information about tourist destinations used by the recommendation system.

The dataset supports filtering and personalized destination discovery.

---

## 🎯 Project Objectives

1. Promote tourism in Pakistan.
2. Help users discover tourist destinations.
3. Provide personalized travel recommendations.
4. Apply Machine Learning to tourism.
5. Make travel planning more convenient.
6. Collect user feedback to support future improvements.

---

## 🚀 Future Improvements

Possible future enhancements include:

- User registration and login.
- Interactive maps and location-based recommendations.
- Weather-based travel suggestions.
- Hotel and transport recommendations.
- Improved recommendation algorithms.
- Cloud deployment and online accessibility.
- More tourism datasets covering additional cities across Pakistan.

---

## 👩‍💻 Project Information

**Project Name:** TravelMate Pakistan  
**Project Type:** AI-Based Tourism Recommendation System  
**Domain:** Artificial Intelligence, Machine Learning and Tourism  
**Backend:** FastAPI  
**Frontend:** HTML, CSS, JavaScript and Streamlit  
**Database:** SQLite  

---

## ❤️ Acknowledgment

TravelMate Pakistan is developed to encourage tourism and make discovering Pakistan's beautiful destinations easier through technology and Artificial Intelligence.

**Explore Pakistan. Discover More. Travel Smarter! 🇵🇰**

---

*Note: This README describes the current project structure and implemented features. Actual recommendation behavior depends on the trained model, dataset, and recommender implementation.*

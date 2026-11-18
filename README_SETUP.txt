TRAVELMATE PAKISTAN — FASTAPI WEBSITE

IMPORTANT: This is an integration folder. Keep your existing project files and folders.
Copy the complete "website" folder into the root of your existing DatascienceProject.

Your final layout should look like:
DatascienceProject/
  app.py
  dataset/travelmate_pakistan_tourist_places.csv
  images/                         (KEEP ALL YOUR EXISTING PLACE PHOTOS HERE)
  recommender.py/recommender.py
  sqlite database/database.py
  sqlite database/feedback.db     (created automatically if it does not exist)
  models/random_forest_model.pkl
  website/
    main.py
    requirements-website.txt
    README_SETUP.txt
    static/
      index.html
      explore.html
      about.html
      style.css
      app.js

RUN ON WINDOWS:
1. Open Command Prompt / terminal in DatascienceProject root.
2. Install website dependencies:
   pip install -r website/requirements-website.txt
3. Start website:
   python -m uvicorn website.main:app --reload
4. Open:
   http://127.0.0.1:8000

PAGES:
  /         Home
  /explore  Destination search, recommendations and feedback
  /about    About and technology information

NOTES:
- Existing Streamlit app.py is not deleted or modified. You can still run it separately.
- The FastAPI website imports your existing recommend_places() and database functions.
- Your images folder is mounted at /images. The hero uses images/mountain_banner1.jpg.
- Destination image filenames are matched automatically against place names. If a particular CSV place name differs significantly from its image filename, that one card may show the gradient fallback; rename the image to a similar place name or add a matching filename.
- The backend expects the dataset columns used by your current app: place_name, city, category, description, interests, entry_fee, latitude, longitude, rating.
- If you get "No module named recommender" or "No module named database", verify the exact folder names and placement shown above.
- If the website starts but says dataset not found, ensure you launched uvicorn from the DatascienceProject root and the dataset filename is exact.
- Feedback is saved using your existing SQLite database.py functions. No separate feedback.py file is required.

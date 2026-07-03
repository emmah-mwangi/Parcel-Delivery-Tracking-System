# Parcel Delivery Tracking System - Frontend & Backend Completion

This branch contains a completed Flask backend, a professional frontend (HTML/CSS/JS), and implementations for the cost calculator and reports modules. The Flask app is at backend/app.py and serves the frontend from the frontend/ directory.

How to run locally:

1. Create and activate a virtual environment (optional but recommended):
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate    # Windows

2. Install dependencies:
   pip install -r requirements.txt

3. Run the Flask app:
   python backend/app.py

Open http://localhost:5000 in your browser.

Notes:
- The backend will attempt to import existing project modules (Parcel_CostCalculator, Parcel_Reports). If they exist, they will be used; otherwise the included implementations will be used.
- Data is stored in backend/data/ as JSON files so the repo remains simple to run locally.

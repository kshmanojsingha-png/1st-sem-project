# ReviewSense - Frontend UI Dashboard

High-performance Streamlit SaaS dashboard for Aspect-Based Customer Review & Sentiment Intelligence.

---

## 🚀 Quick Start (Local)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

> **Tip:** If the FastAPI backend is running locally on port 8000, the frontend automatically connects to it. If the backend is not running, the dashboard automatically activates the built-in offline fallback.

---

## ☁️ Publishing to Streamlit Community Cloud (Free)

Deploy your live web application to the cloud in 5 simple steps:

### Step 1: Push to GitHub
Make sure this repository (or standalone `frontend` repo) is pushed to your GitHub account:
```bash
git add .
git commit -m "feat: complete frontend dashboard"
git push origin main
```

### Step 2: Open Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
2. Click **Create app** -> **I already have an app**.

### Step 3: Configure Deployment
- **Repository**: `your-username/1st-sem-project` (or your repo name)
- **Branch**: `main`
- **Main file path**: `frontend/app.py` (or `app.py` if `frontend` is its own repository)
- **App URL**: choose your custom subdomain (e.g. `reviewsense.streamlit.app`)

### Step 4: Connect to Your Live Backend (Optional / Recommended)
If you published your backend on Render/Railway/Fly.io:
1. Click **Advanced settings...**
2. In the **Secrets** box, paste your live backend URL:
   ```toml
   BACKEND_URL = "https://your-backend-api.onrender.com"
   ```
3. Alternatively, users can paste the live backend URL directly into the **Backend API URL** field in the sidebar!

### Step 5: Click Deploy! 🎈
Streamlit Cloud will install dependencies from `requirements.txt` and launch your live application at your public URL.

---

## 📁 Folder Structure

```
frontend/
├── .streamlit/
│   └── config.toml           # Streamlit theme & server configuration
├── data/
│   └── predictions.csv       # Test dataset (6k reviews) for Evaluation tab
├── final_food_reviews.csv    # 50k Amazon reviews for Catalog Explorer
├── app.py                    # Main Streamlit dashboard application
├── api_client.py             # HTTP client connecting to FastAPI backend
├── ui_charts.py              # Plotly chart visualizations
├── ui_theme.py               # Dark mode styling & UI design system
├── aspect_detection.py       # Aspect keyword detection engine
├── requirements.txt          # Lightweight frontend dependencies
└── README.md                 # This guide
```

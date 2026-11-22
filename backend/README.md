# ReviewSense - Backend API Service

FastAPI-powered Aspect-Based Sentiment Analysis microservice running the trained scikit-learn TF-IDF + Logistic Regression pipeline.

---

## 🚀 Quick Start (Local)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
uvicorn api:app --reload --port 8000
```
Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** to test interactive Swagger API documentation.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service health, version, and endpoints overview |
| `GET` | `/health` | Health check (`{"status": "ok", "predictor_available": true}`) |
| `POST` | `/predict` | Single review prediction (`review_text`) |
| `POST` | `/predict_batch` | Batch review predictions (`{"reviews": [{"review_text": "..."}]}`) |

### Example Request (`/predict`)
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"review_text": "The build quality is amazing and delivery was super fast!"}'
```

### Example Response
```json
{
  "sentiment": "positive",
  "aspects": ["Quality", "Shipping"],
  "confidence": 0.9609,
  "probabilities": {
    "negative": 0.0222,
    "neutral": 0.0169,
    "positive": 0.9609
  }
}
```

---

## ☁️ Publishing & Deployment

### Option 1: Deploy on Render (Recommended - Free)
1. Push this repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following fields:
   - **Root Directory**: `backend` (if deploying from a monorepo) or leave empty if `backend` is its own repo.
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**.
6. Once deployed, copy your Render URL (e.g. `https://reviewsense-api.onrender.com`). You will pass this URL to the frontend!

### Option 2: Deploy on Railway
1. Sign in to [Railway.app](https://railway.app).
2. Select **Deploy from GitHub repo**.
3. Set root directory to `backend/`. Railway will automatically detect the `Procfile` and deploy.

### Option 3: Deploy with Docker
```bash
docker build -t reviewsense-api .
docker run -p 8000:8000 reviewsense-api
```
Compatible with any cloud host supporting Docker (Render, Railway, Fly.io, Hugging Face Spaces Docker, AWS ECS).

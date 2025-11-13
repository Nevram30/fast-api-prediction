# ⚡ Quick Start Guide

Get your FastAPI ML Service running in 5 minutes!

## 🎯 Prerequisites

- Python 3.11+
- pip
- Your trained ML models (`.pkl` files)

## 🚀 Local Development (5 Steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your Models

Place your trained models in the `models/` directory:

```bash
models/
├── tilapia_forecast_best_model.pkl
└── bangus_forecast_best_model.pkl
```

### 3. Set Up Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (optional for local development)
```

### 4. Run the Service

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Test It!

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🧪 Test the API

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click on `POST /api/v1/predict`
3. Click "Try it out"
4. Enter test data:
   ```json
   {
     "species": "tilapia",
     "dateFrom": "2024-01-01",
     "dateTo": "2024-01-31",
     "province": "Pampanga",
     "city": "Mexico"
   }
   ```
5. Click "Execute"

### Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "species": "tilapia",
    "dateFrom": "2024-01-01",
    "dateTo": "2024-01-31",
    "province": "Pampanga",
    "city": "Mexico"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/predict',
    json={
        'species': 'tilapia',
        'dateFrom': '2024-01-01',
        'dateTo': '2024-01-31',
        'province': 'Pampanga',
        'city': 'Mexico'
    }
)

print(response.json())
```

## 🌐 Deploy to Railway (3 Steps)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects Dockerfile and deploys!

### 3. Configure & Test

1. Add environment variable:
   ```
   ENVIRONMENT=production
   ```
2. Generate domain in Railway settings
3. Test: `https://your-service.railway.app/docs`

## 📱 Connect to Next.js

Add to your Next.js `.env.local`:

```env
ML_SERVICE_URL=http://localhost:8000
# Or for production:
# ML_SERVICE_URL=https://your-service.railway.app
```

Create API route:

```typescript
// app/api/forecast/route.ts
export async function POST(request: Request) {
  const body = await request.json();
  
  const response = await fetch(`${process.env.ML_SERVICE_URL}/api/v1/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  
  return Response.json(await response.json());
}
```

## 🎉 You're Done!

Your ML service is now running and ready to serve predictions!

### Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🚀 Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guide
- 🔧 Customize `app/predictor.py` to match your model's features
- 📊 Monitor your service in Railway dashboard

## 🆘 Common Issues

### Models not loading?
- Check that `.pkl` files are in `models/` directory
- Verify file names match configuration

### Port already in use?
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Import errors?
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Railway Docs](https://docs.railway.app)
- [Full Documentation](README.md)

---

Need help? Open an issue on GitHub!

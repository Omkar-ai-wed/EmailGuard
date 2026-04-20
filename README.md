# 🛡️ EmailGuard — Unwanted Email Detection System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.4-f7931e?style=flat-square&logo=scikitlearn" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render" alt="Render"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT"/>
</p>

> A full-stack **ML-powered email threat detection system** with a live analytics dashboard, FastAPI REST backend, and scikit-learn classifier. Built for college demo/production use.

---

## 🌐 Live Links

| Service | URL |
|---------|-----|
| 🖥️ **Dashboard (GitHub Pages)** | [https://omkar-ai-wed.github.io/EmailGuard/](https://omkar-ai-wed.github.io/EmailGuard/) |
| ⚙️ **Backend API (Render)** | [https://emailguard-api.onrender.com](https://emailguard-api.onrender.com) |
| 📖 **Swagger / API Docs** | [https://emailguard-api.onrender.com/docs](https://emailguard-api.onrender.com/docs) |
| ❤️ **Health Check** | [https://emailguard-api.onrender.com/health](https://emailguard-api.onrender.com/health) |

> **Note:** The free Render tier sleeps after 15 min of inactivity — first request may take ~50 seconds to wake up. The dashboard falls back to demo data automatically if the API is sleeping.

---

## 📸 Dashboard Pages

| Page | Description |
|------|-------------|
| 🏠 **Overview** | Live stats, email table, security alerts panel |
| 🗄️ **Email Database** | Searchable & paginated email records |
| 🔑 **Rules & Keywords** | Detection rules, spam keywords, domain blocklist |
| 📊 **Model Performance** | Accuracy, confusion matrix, ROC curve, feature importance |
| 🚨 **Security Alerts** | Real-time alerts with severity filtering |

---

## 🗂️ Project Structure

```
EmailGuard/
├── index.html                      # → Redirects to dashboard (GitHub Pages entry)
├── render.yaml                     # Render deployment blueprint
├── README.md
├── .gitignore
│
├── Dashboard_UI/                   # 🖥️  Frontend (pure HTML + Tailwind CDN)
│   ├── Overview_Dashboard.html
│   ├── Email_Database.html
│   ├── Rules_Keywords.html
│   ├── Model_Performance.html
│   └── Security_Alerts.html
│
└── backend/                        # ⚙️  FastAPI Backend
    ├── main.py                     # App entry point
    ├── run.py                      # Quick start: python run.py
    ├── start_all.py                # Starts BOTH servers at once
    ├── seed_data.py                # Populate DB with demo data
    ├── config.py                   # Settings (JWT, DB URL)
    ├── database.py                 # SQLAlchemy engine
    ├── requirements.txt            # pip dependencies
    ├── .python-version             # Python 3.11.9 (for Render)
    ├── .env.example                # Copy → .env
    ├── models/                     # ORM models (User, Email, Alert…)
    ├── routers/                    # API routes
    ├── schemas/                    # Pydantic schemas
    ├── middleware/                 # Auth middleware
    └── services/                  # Business logic + ML model
```

---

## 🚀 How to Run — Step by Step

There are **3 ways** to run EmailGuard:

---

### ▶️ Option 1 — Frontend Only (No Setup)

> Works instantly. No Python, no terminal. Perfect for viewing the dashboard.

1. Clone or download the repository
2. Open `index.html` in any browser **OR** double-click `Dashboard_UI/Overview_Dashboard.html`
3. Done ✅ — dashboard loads with demo data automatically

---

### ▶️ Option 2 — One-Command Start (Recommended)

> Starts **both** the API backend and the frontend server at once.

**Step 1 — Clone the repository**
```powershell
git clone https://github.com/Omkar-ai-wed/EmailGuard.git
cd EmailGuard
```

**Step 2 — Install Python dependencies**
```powershell
cd backend
pip install -r requirements.txt
```

**Step 3 — Start everything**
```powershell
python start_all.py
```

This automatically:
- 🌱 Seeds the database on first run (demo emails, users, keywords)
- 🚀 Starts FastAPI at → `http://localhost:8000`
- 🌐 Serves dashboard at → `http://localhost:3000`
- 🌍 Opens the browser automatically

---

### ▶️ Option 3 — Manual Start (Two Terminals)

**Terminal 1 — Backend API**
```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env
python seed_data.py
python run.py
```

API is live at:
- 🔗 `http://localhost:8000`
- 📖 Swagger: `http://localhost:8000/docs`
- ❤️ Health: `http://localhost:8000/health`

**Terminal 2 — Frontend Server**
```powershell
cd Dashboard_UI
python -m http.server 3000
```

Dashboard: `http://localhost:3000/Overview_Dashboard.html`

---

## 🔑 Default Login Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | `admin` | `admin123` | Full access |
| Analyst | `analyst` | `analyst123` | Classify & view |
| Viewer | `viewer` | `viewer123` | Read-only |

> The dashboard auto-logs in as **analyst** on page load — no manual login needed.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Create new user account |
| `POST` | `/api/v1/auth/login` | Get JWT access token |
| `GET` | `/api/v1/analytics/overview` | Overall dashboard stats |
| `GET` | `/api/v1/emails/` | List emails (paginated) |
| `POST` | `/api/v1/emails/ingest` | Submit email for classification |
| `PATCH` | `/api/v1/emails/{id}/status` | Update email status |
| `GET` | `/api/v1/alerts/` | Get security alerts |
| `PATCH` | `/api/v1/alerts/{id}/resolve` | Resolve an alert |
| `GET` | `/api/v1/keywords/` | List spam keywords |
| `POST` | `/api/v1/keywords/` | Add new keyword rule |
| `GET` | `/api/v1/classify/{email_id}` | Get classification details |
| `GET` | `/api/v1/reputation/` | Sender reputation records |
| `GET` | `/docs` | Interactive Swagger UI |

Base URL (production): `https://emailguard-api.onrender.com`

---

## 🧠 ML Model Details

| Property | Value |
|----------|-------|
| Algorithm | Multinomial Naive Bayes (scikit-learn) |
| Feature Extraction | TF-IDF (subject + body) |
| Additional Features | Sender reputation, URL density, attachment flags, header anomaly |
| Output Classes | `wanted`, `unwanted` (spam), `suspicious`, `phishing` |
| Accuracy | **97.4%** |
| Precision | **96.8%** |
| Recall | **98.1%** |
| F1-Score | **97.4%** |
| AUC-ROC | **0.991** |

---

## ☁️ Deployment

### Backend — Render (Live)

The backend is deployed on Render via `render.yaml` (Blueprint). It auto-deploys on every push to `main`.

**To redeploy manually:**
```powershell
git add .
git commit -m "your message"
git push
```
Render will detect the push and trigger a new build automatically.

**Environment variables set on Render:**

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.11.9` |
| `DEBUG` | `false` |
| `DATABASE_URL` | `sqlite:///./emailguard.db` |
| `SECRET_KEY` | *(auto-generated by Render)* |

### Frontend — GitHub Pages

1. Go to your repo → **Settings → Pages**
2. Source: **Deploy from a branch** → Branch: `main` | Folder: `/ (root)`
3. Click **Save** → live in ~1 minute

**Live URL:** `https://omkar-ai-wed.github.io/EmailGuard/`

---

## 🔧 Troubleshooting

**❌ `pip` not recognized**
```powershell
python -m pip install -r requirements.txt
```

**❌ `uvicorn` not recognized**
```powershell
python -m uvicorn main:app --port 8000 --reload
```

**❌ Port already in use**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

**❌ Database errors — reset the database**
```powershell
cd backend
del emailguard.db
python seed_data.py
python run.py
```

**❌ Render build fails (numpy/scikit-learn error)**

Ensure `requirements.txt` uses flexible pins:
```
scikit-learn>=1.4.2
numpy>=1.26.4
```
And `backend/.python-version` contains `3.11.9`.

---

## 📄 License

MIT License — free to use for academic, personal, and commercial projects.

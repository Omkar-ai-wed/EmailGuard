# 🛡️ EmailGuard — Unwanted Email Detection System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.4-f7931e?style=flat-square&logo=scikitlearn" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite" alt="SQLite"/>
  <img src="https://img.shields.io/badge/TailwindCSS-CDN-38bdf8?style=flat-square&logo=tailwindcss" alt="Tailwind"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT"/>
</p>

> A full-stack **ML-powered email threat detection system** with a live analytics dashboard, FastAPI REST backend, and scikit-learn classifier. Built for college demo/production use.

---

## 🌐 Live Demo (GitHub Pages)

**▶ [View Dashboard](https://omkar-ai-wed.github.io/EmailGuard/)**

> The dashboard runs in **demo mode** with realistic sample data when the backend is offline — no setup needed to view it!

---

## 📸 Dashboard Pages

| Page | Description |
|---|---|
| 🏠 **Overview** | Live stats, email table, security alerts panel |
| 🗄️ **Email Database** | Searchable paginated email records |
| 🔑 **Rules & Keywords** | Detection rules, spam keywords, domain blocklist |
| 📊 **Model Performance** | Accuracy, confusion matrix, ROC curve, feature importance |
| 🚨 **Security Alerts** | Real-time alerts with severity filtering |

---

## 🗂️ Project Structure

```
EmailGuard/
├── index.html                      # → Redirects to dashboard (GitHub Pages entry)
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
    ├── .env.example                # Copy → .env
    ├── models/                     # ORM models (User, Email, Alert…)
    ├── routers/                    # API routes
    ├── schemas/                    # Pydantic schemas
    ├── middleware/                 # Auth middleware
    └── services/                   # Business logic + ML model
```

---

## 🚀 How to Run — Step by Step

There are **3 ways** to run EmailGuard depending on what you need:

---

### ▶️ Option 1 — Frontend Only (No Setup)

> Works instantly. No Python, no terminal. Perfect for viewing the dashboard.

1. Clone or download the repository
2. Open `index.html` in any browser **OR** double-click `Dashboard_UI/Overview_Dashboard.html`
3. Done ✅ — dashboard loads with demo data automatically

---

### ▶️ Option 2 — One-Command Start (Recommended)

> Starts **both** the API backend and the frontend server at once. Opens browser automatically.

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

**Step 3 — Start everything with one command**
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

> Best for development — run backend and frontend in separate terminals.

**Terminal 1 — Backend API**

```powershell
# Navigate to backend folder
cd d:\play\Email\backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Copy environment file (first time only)
copy .env.example .env

# Seed the database with demo data (first time only)
python seed_data.py

# Start the FastAPI backend
python run.py
```

The API is now live at:
- 🔗 API Base: `http://localhost:8000`
- 📖 Swagger Docs: `http://localhost:8000/docs`
- 📋 ReDoc: `http://localhost:8000/redoc`
- ❤️ Health Check: `http://localhost:8000/health`


**Terminal 2 — Frontend Server**

```powershell
# Navigate to frontend folder
cd d:\play\Email\Dashboard_UI

# Start built-in Python HTTP server
python -m http.server 3000
```

The dashboard is now live at:
- 🌐 Dashboard: `http://localhost:3000/Overview_Dashboard.html`


**Then open your browser to:**
```
http://localhost:3000/Overview_Dashboard.html
```

---

## 🔑 Default Login Credentials

| Role | Username | Password | Access Level |
|---|---|---|---|
| Admin | `admin` | `admin123` | Full access |
| Analyst | `analyst` | `analyst123` | Classify & view |
| Viewer | `viewer` | `viewer123` | Read-only |

> The dashboard auto-logs in as **analyst** on page load — no manual login needed.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
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

---

## 🧠 ML Model Details

| Property | Value |
|---|---|
| Algorithm | Multinomial Naive Bayes (scikit-learn) |
| Feature Extraction | TF-IDF (subject + body) |
| Additional Features | Sender reputation, URL density, attachment flags, header anomaly |
| Output Classes | `wanted`, `unwanted` (spam), `suspicious`, `phishing` |
| Accuracy | **97.4%** |
| Precision | **96.8%** |
| Recall | **98.1%** |
| F1-Score | **97.4%** |
| AUC-ROC | **0.991** |
| Training Samples | 50,000 emails |

---

## 🌐 Deploy to GitHub Pages

Enable the live demo in 2 minutes:

**Step 1 — Push to GitHub**
```powershell
cd d:\play\Email
git init
git add .
git commit -m "Initial commit: EmailGuard dashboard"
git branch -M main
git remote add origin https://github.com/Omkar-ai-wed/EmailGuard.git
git push -u origin main
```

If your repository is already initialized and you only need to push Render deployment updates:
```bash
git add render.yaml backend/run.py Dashboard_UI/
git commit -m "chore: add Render deployment config"
git push
```
This snippet (shown in image2, Step 1 — Push to GitHub) stages `render.yaml`, `backend/run.py`, and `Dashboard_UI/`, commits with `chore: add Render deployment config`, then pushes the commit to GitHub.

**Step 2 — Enable GitHub Pages**
1. Go to your repo: `https://github.com/Omkar-ai-wed/EmailGuard`
2. Click **Settings** → **Pages** (left sidebar)
3. Under **Source** → select **Deploy from a branch**
4. Branch: **main** | Folder: **/ (root)**
5. Click **Save**
6. Wait ~1 minute → your site is live! 🎉

**Your live URL:**
```
https://omkar-ai-wed.github.io/EmailGuard/
```

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
# Kill process on port 8000
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

**❌ Git push rejected (remote already has commits)**
```powershell
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## 📄 License

MIT License — free to use for academic, personal, and commercial projects.

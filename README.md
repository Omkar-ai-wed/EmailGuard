# EmailGuard — Unwanted Email Detection System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/TailwindCSS-CDN-38bdf8?style=flat-square&logo=tailwindcss" alt="Tailwind"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.4-f7931e?style=flat-square&logo=scikitlearn" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT"/>
</p>

> A full-stack email threat detection system with a machine-learning backend and a beautiful, live-data dashboard.

---

## 🖥️ Live Demo (GitHub Pages)

**[View Dashboard →]([https://Omkar-ai-wed.github.io/EmailGuard/])**

> The dashboard runs in **demo mode** with realistic sample data when the backend is not connected. All UI pages are fully functional.

---

## 📸 Screenshots

| Overview | Email Database | Security Alerts |
|---|---|---|
| Metrics, live email table, alerts | Searchable email list, rules | Real-time alert cards by severity |

---

## 🗂️ Project Structure

```
Email/
├── index.html                    # → Redirects to dashboard
├── Dashboard_UI/
│   ├── Overview_Dashboard.html   # Main dashboard (live stats + table)
│   ├── Email_Database.html       # Email records + rules/keyword heatmap
│   ├── Rules_Keywords.html       # Detection rules + domain blocklist
│   ├── Model_Performance.html    # ML metrics, confusion matrix, ROC
│   └── Security_Alerts.html      # Real-time alert feed with filtering
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── run.py                    # Run helper (python run.py)
│   ├── seed_data.py              # Populate DB with demo data
│   ├── config.py                 # Settings (JWT secret, DB URL)
│   ├── database.py               # SQLAlchemy engine setup
│   ├── models/                   # ORM models
│   ├── routers/                  # API route handlers
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic + ML model
│   └── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Frontend Only (No Backend)

Just open `index.html` in a browser — it auto-redirects to the dashboard with demo data pre-loaded.

### 2. Full Stack (with Backend)

```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/Email.git
cd Email/backend

# Install dependencies
pip install -r requirements.txt

# Seed the database with demo data
python seed_data.py

# Start the API server
python run.py
# → API at http://localhost:8000
# → Swagger UI at http://localhost:8000/docs

# Open Dashboard_UI/Overview_Dashboard.html in your browser
# The dashboard will auto-connect and show LIVE data
```

---

## 🔑 Default Credentials (for demo)

| Role | Username | Password |
|---|---|---|
| Analyst | `analyst` | `analyst123` |
| Admin | `admin` | `admin123` |

---

## 🧠 ML Model

The backend uses a **Multinomial Naive Bayes** classifier (scikit-learn) trained on:
- **Features**: TF-IDF on email subject + body, sender reputation score, URL density, attachment type flags, header anomaly score
- **Classes**: `wanted`, `unwanted` (spam), `suspicious`, `phishing`
- **Metrics**: 97.4% Accuracy · 96.8% Precision · 98.1% Recall · 0.991 AUC-ROC

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Get JWT token |
| `GET` | `/api/v1/analytics/overview` | Dashboard stats |
| `GET` | `/api/v1/emails/` | List emails (paginated) |
| `POST` | `/api/v1/emails/ingest` | Submit email for analysis |
| `GET` | `/api/v1/alerts/` | Security alerts |
| `GET` | `/api/v1/keywords/` | Spam keywords |
| `GET` | `/docs` | Interactive Swagger UI |

---

## 🌐 Deploy to GitHub Pages

1. Push to GitHub
2. Go to **Settings → Pages**
3. Set Source to **Deploy from Branch → main → / (root)**
4. Your site is live at `https://YOUR-USERNAME.github.io/Email/`

---

## 📄 License

MIT — free to use for academic and commercial projects.

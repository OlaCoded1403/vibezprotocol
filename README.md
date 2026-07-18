# Vibez Protocol — Full Project
### Author: Oyeyemi Olamilekan

---

## Project Structure

```
vibezprotocol/
├── frontend/
│   ├── index.html       ← Main website
│   ├── style.css        ← All styles
│   └── script.js        ← Connects to backend API
│
├── backend/
│   ├── app/
│   │   ├── main.py      ← FastAPI entry point
│   │   ├── database.py  ← DB connection
│   │   ├── models.py    ← DB tables
│   │   ├── schemas.py   ← Validation
│   │   ├── auth.py      ← JWT + passwords
│   │   └── routes/
│   │       ├── auth.py      ← Login + setup
│   │       ├── contact.py   ← Contact form
│   │       ├── projects.py  ← Portfolio
│   │       └── admin.py     ← Admin endpoints
│   ├── static/
│   │   └── admin.html   ← Admin dashboard UI
│   ├── requirements.txt
│   ├── .env.example     ← 🔑 Copy to .env and fill in
│   └── README.md        ← Full backend docs
│
├── .gitignore
└── README.md            ← You are here
```

---

## Quick Start

### Terminal 1 — Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # then fill in your 🔑 keys
uvicorn app.main:app --reload
```

### Terminal 2 — Frontend
```bash
# In VSCode: right-click frontend/index.html → Open with Live Server
```

- Frontend: http://localhost:5500 (Live Server default)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Dashboard: http://localhost:8000/admin

---

## VSCode Tips

- Open the `vibezprotocol` root folder in VSCode — you'll see both frontend and backend in the sidebar
- Use the built-in **Split Terminal** to run backend and frontend side by side
- Install these VSCode extensions:
  - **Live Server** — preview frontend instantly
  - **Python** — backend syntax + debugging
  - **Thunder Client** — test API endpoints without leaving VSCode
  - **Pylance** — Python intellisense

---

© 2025 Vibez Protocol — Oyeyemi Olamilekan

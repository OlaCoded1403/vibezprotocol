# Vibez Protocol — Backend API
### Author: Oyeyemi Olamilekan

---

## Project Structure

```
vibezprotocol-backend/
├── app/
│   ├── __init__.py
│   ├── main.py            ← App entry point + route registration
│   ├── database.py        ← DB connection (SQLite local / PostgreSQL deploy)
│   ├── models.py          ← DB table definitions
│   ├── schemas.py         ← Request/response validation
│   ├── auth.py            ← JWT tokens + password hashing
│   └── routes/
│       ├── auth.py        ← POST /api/auth/login & /setup
│       ├── contact.py     ← POST /api/contact
│       ├── projects.py    ← GET/POST/PUT/DELETE /api/projects
│       └── admin.py       ← Admin stats + inquiry management
├── static/
│   └── admin.html         ← Admin dashboard UI (no framework)
├── requirements.txt
├── .env.example           ← 🔑 Copy to .env and fill in your keys
└── README.md
```

---

## Local Setup

### Step 1 — Open project in VSCode
```bash
cd vibezprotocol-backend
code .
```

### Step 2 — Create and activate a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set up your .env file
```bash
# Duplicate the example file
cp .env.example .env
```
Open `.env` and fill in every field marked 🔑

### Step 5 — Run the server
```bash
uvicorn app.main:app --reload
```

| URL | What it does |
|-----|--------------|
| http://localhost:8000 | Health check |
| http://localhost:8000/docs | Interactive API docs (test everything here) |
| http://localhost:8000/admin | Admin dashboard UI |

---

## First-Time Admin Setup (Run Once)

After starting the server, go to:
**http://localhost:8000/docs** → find **/api/auth/setup** → click "Try it out"

Fill in:
- `setup_key`: whatever you put in `.env` as `SETUP_SECRET`
- Body: `{ "username": "olamilekan", "password": "🔑 your chosen password" }`

Click Execute. Done — your admin account is created.
Now log in at **http://localhost:8000/admin**

---

## Gmail App Password Setup

So you receive email alerts when someone submits the contact form:

1. Go to **myaccount.google.com**
2. **Security** → enable **2-Step Verification**
3. Search **"App Passwords"**
4. Create one → App: Mail → Device: Other → name it "Vibez Protocol"
5. Copy the 16-character password (no spaces) into `.env` as `GMAIL_APP_PASSWORD`

---

## API Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | / | Public | Health check |
| GET | /docs | Public | Auto API docs |
| GET | /admin | Public URL | Admin UI |
| POST | /api/auth/login | Public | Get JWT token |
| POST | /api/auth/setup | Setup key | Create admin (once) |
| POST | /api/contact | Public | Submit contact form |
| GET | /api/projects | Public | All visible projects |
| GET | /api/projects/{id} | Public | Single project |
| POST | /api/projects | Admin | Add project |
| PUT | /api/projects/{id} | Admin | Edit project |
| DELETE | /api/projects/{id} | Admin | Delete project |
| GET | /api/admin/stats | Admin | Dashboard numbers |
| GET | /api/admin/inquiries | Admin | All form submissions |
| PUT | /api/admin/inquiries/{id}/read | Admin | Mark as read |
| DELETE | /api/admin/inquiries/{id} | Admin | Delete inquiry |

---

## Deploying to Render (Free)

1. Push the `vibezprotocol-backend` folder to a **GitHub repo**
2. Go to **render.com** → New → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variables** in Render dashboard:
   - `DATABASE_URL` → your Render PostgreSQL URL (add a free Postgres DB from Render)
   - `SECRET_KEY` → run `python -c "import secrets; print(secrets.token_hex(32))"` and paste result
   - `GMAIL_USER` → vibezprotocol@gmail.com
   - `GMAIL_APP_PASSWORD` → your Gmail App Password
   - `SETUP_SECRET` → your chosen setup key
6. Deploy — your API is live at `https://your-app.onrender.com`

After deploying:
- Update `API_URL` in the frontend `script.js` to your Render URL
- Update `API` in `static/admin.html` to your Render URL (marked with 🔑)
- Run the `/api/auth/setup` endpoint once on the live server

---

## Adding the AI Chatbot Later

When your Python chatbot is ready, it plugs straight in:

```python
# 1. Create app/routes/chatbot.py
from fastapi import APIRouter
router = APIRouter()

@router.post("/chat")
async def chat(message: str):
    # your AI logic here
    return {"reply": "..."}

# 2. In app/main.py, add:
from app.routes import chatbot
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
```

Same server. Same language. Zero extra infrastructure.

---

© 2025 Vibez Protocol — Oyeyemi Olamilekan

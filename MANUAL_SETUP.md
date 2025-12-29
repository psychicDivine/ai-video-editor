# Manual Setup - AI Video Editor

**Step-by-step manual installation**

---

## Step 1: Backend Setup

```powershell
cd c:\Office\editor\backend

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install UV
pip install uv

# Install dependencies
uv pip install -e ".[dev]"
```

**Expected output:** "Successfully installed..." messages

---

## Step 2: Frontend Setup

```powershell
cd c:\Office\editor\frontend

# Install dependencies
npm install
```

**Expected output:** "added X packages" message

---

## Step 3: Start Backend

```powershell
cd c:\Office\editor\backend

# Activate venv if not already
.\venv\Scripts\activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:** "Uvicorn running on http://0.0.0.0:8000"

---

## Step 4: Start Frontend (New Terminal)

```powershell
cd c:\Office\editor\frontend

# Start dev server
npm run dev
```

**Expected output:** "VITE v5.x.x ready in XXX ms"

---

## Step 5: Verify

Open in browser:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ✅ Done!

Both services running. Ready to start development.

---

## Troubleshooting

### Backend won't start
```powershell
cd backend
.\venv\Scripts\activate
pip list  # Check if packages installed
```

### Frontend won't start
```powershell
cd frontend
npm list  # Check if packages installed
```

### Port already in use
- Change port in uvicorn command: `--port 8001`
- Or kill process using port 8000/3000

---

**Next:** Start building PHASE 2 (Frontend UI)

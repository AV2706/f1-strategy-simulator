# IBM skillsbuild — Build Instructions

This workspace contains two primary parts:

- Frontend: a Vite + React app in `Frontend/`
- Backend: a FastAPI app in `integration/`

This README provides commands to produce production builds and a quick local verification.

## Prerequisites
- Node.js 18+ and npm installed
- Python 3.9+ (with `venv`) installed

## Build frontend (production)

```powershell
cd Frontend
npm ci
npm run build
# Optional: preview the built site
npm run preview
```

The production build output is `Frontend/dist/`.

## Prepare backend

```powershell
cd integration
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
# Run development server
.\.venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Orchestrated single-step build (Windows PowerShell)

Run the provided `build.ps1` script from the repo root to build frontend and prepare the backend venv.

```powershell
.\build.ps1
```

If you want Docker support or CI workflows added, tell me and I'll add Dockerfiles and GitHub Actions workflows.

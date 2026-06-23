# Backero — Viral Video Production Form API

**Python 3.11+ | FastAPI | Supabase | Pydantic v2**

## Quick Start (Windows)

```
1. Download this folder to your computer
2. Double-click start.bat
3. Open http://localhost:8000 in your browser
4. Click "Run Full Integration Test" to verify everything works
```

## Quick Start (Mac/Linux)

```bash
cd backend
chmod +x start.sh
./start.sh
# Open http://localhost:8000
```

## Connect Your Frontend

Your React frontend at `https://rbcm2h5ijpzgq.kimi.page` needs to know the backend URL.

**Option A — Run frontend locally (recommended for dev):**

```bash
# In your frontend project folder:
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
# Frontend runs on http://localhost:5173, calls backend at http://localhost:8000
```

**Option B — Add proxy in vite.config.ts:**

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

**Option C — Deploy backend (production):**

Push this folder to GitHub → deploy on Railway/Render → set `VITE_API_URL` to the deployed URL.

## API Endpoints (53 routes)

| Group       | Base Path          | Endpoints |
|-------------|-------------------|-----------|
| Dashboard   | `/api/dashboard`   | 6         |
| Phase 1     | `/api/phase1`      | 7         |
| Phase 2     | `/api/phase2`      | 6         |
| Phase 3     | `/api/phase3`      | 6         |
| Phase 4     | `/api/phase4`      | 7         |
| Phase 5     | `/api/phase5`      | 5         |
| Phase 6     | `/api/phase6`      | 10        |
| Utility     | `/health`, `/docs` | 6         |

Full interactive docs at **http://localhost:8000/docs**

## Supabase

Database is already configured on your BACKERO project (`xiamoqbknvytiotmujfj`).
All 7 tables + RLS policies + triggers are set up.

If you need to add the service role key for extra permissions:
1. Go to Supabase → BACKERO → Settings → API
2. Copy the `service_role` secret key
3. Paste it as `SUPABASE_SERVICE_KEY` in `.env`

## Project Structure

```
backend/
├── main.py                    # FastAPI app + test dashboard
├── .env                       # Supabase credentials (pre-filled)
├── requirements.txt           # Python dependencies
├── start.bat                  # Windows one-click launcher
├── start.sh                   # Mac/Linux launcher
├── Procfile                   # Railway/Render deployment
├── runtime.txt                # Python version pin
├── db/
│   ├── supabase_client.py     # Supabase singleton client
│   └── schema.sql             # Database schema (already applied)
├── models/                    # Pydantic v2 data models
│   ├── shared.py              # BriefStatus, APIResponse
│   ├── dashboard.py           # Metrics, Pipeline, BriefList
│   ├── phase1.py              # KnowledgeNugget, HookValidation
│   ├── phase2.py              # FormatStructureCombo, Combos
│   ├── phase3.py              # SceneBeat, Camera, Actor
│   ├── phase4.py              # CheckItem, RoleApproval
│   ├── phase5.py              # ProductionMeta, GoldenRule
│   └── phase6.py              # GraphNode, GraphEdge
├── routers/                   # API route handlers
│   ├── dashboard.py           # /api/dashboard/*
│   ├── phase1.py              # /api/phase1/*
│   ├── phase2.py              # /api/phase2/*
│   ├── phase3.py              # /api/phase3/*
│   ├── phase4.py              # /api/phase4/*
│   ├── phase5.py              # /api/phase5/*
│   └── phase6.py              # /api/phase6/*
└── services/                  # Business logic
    ├── dashboard_service.py   # Metrics, pipeline stats
    ├── phase1_service.py      # Hook validation, nugget extraction
    ├── phase2_service.py      # Correlation map, platform boosts
    ├── phase3_service.py      # Screenplay generation engine
    ├── phase4_service.py      # Quality checks, scoring, verdicts
    ├── phase5_service.py      # Production pack, DOCX export
    └── phase6_service.py      # Node graph, topological sort
```

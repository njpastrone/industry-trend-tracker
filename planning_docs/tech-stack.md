# Tech Stack: Industry Intelligence Tracker

## Architecture

Same proven stack as the sales tracker. No new technologies to learn.

```
Frontend (React)         Backend (FastAPI)        Database (Supabase)
┌──────────────┐        ┌──────────────┐         ┌──────────────┐
│ Vite + React │───────▶│ Python API   │────────▶│ PostgreSQL   │
│ TanStack     │  JSON  │ ETL Pipeline │         │              │
│ Tailwind CSS │        │ Claude Haiku │         │              │
│ React Router │        │ yfinance     │         │              │
└──────────────┘        └──────────────┘         └──────────────┘
     Render                  Render                 Supabase
   Static Site            Web Service               Free Tier
```

### What's the same

| Component | Choice | Reason |
|-----------|--------|--------|
| Frontend framework | React + Vite + TypeScript | Already know it, fast iteration |
| CSS | Tailwind CSS | Already know it, matches design |
| Data fetching | TanStack Query | Already know it, great caching |
| Backend | FastAPI (Python) | Already know it, same patterns |
| Database | Supabase (PostgreSQL) | Free tier, REST API, already have account |
| AI | Claude Haiku | Cheapest, fast, good enough for classification |
| Financial data | yfinance | Already use it, supports ETFs |
| Deployment | Render | Already have account, free tier |

### What's different

| Component | Sales Tracker | Industry Tracker | Why |
|-----------|--------------|-----------------|-----|
| Routing | No router (single page) | React Router | Two pages: dashboard + detail |
| Data sources | Company RSS only | Sector RSS + regulatory feeds | Different scope |
| AI prompts | Company IR pain scoring | Sector signal classification + narratives | Different analysis |
| User data | Profiles, outreach tracking | Minimal (maybe saved preferences) | Monitoring app, not action-tracking |

## Project Structure

```
industry-intelligence-tracker/
├── backend/
│   ├── main.py              # FastAPI routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Router setup
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   └── SectorDetail.tsx
│   │   ├── components/
│   │   │   ├── SectorCard.tsx
│   │   │   ├── SectorGrid.tsx
│   │   │   ├── SignalFeed.tsx
│   │   │   ├── SignalCard.tsx
│   │   │   ├── NarrativeBlock.tsx
│   │   │   ├── SectorHeader.tsx
│   │   │   ├── SignalTypeTabs.tsx
│   │   │   └── Filters.tsx
│   │   ├── api/client.ts
│   │   └── types/index.ts
│   ├── package.json
│   └── vite.config.ts
├── db.py                    # Database operations
├── etl.py                   # Pipeline: fetch, classify, narratives
├── config.py                # Constants, prompts, sector seed data
├── schema.sql               # Database schema
└── seed.sql                 # Sector + feed seed data
```

## Dependencies

### Backend (Python)

```
# requirements.txt
fastapi
uvicorn[standard]
supabase
anthropic
httpx
yfinance
```

Same as the sales tracker. No new dependencies.

### Frontend (TypeScript)

```json
{
  "dependencies": {
    "react": "^19",
    "react-dom": "^19",
    "react-router-dom": "^7",
    "@tanstack/react-query": "^5",
    "axios": "^1"
  },
  "devDependencies": {
    "vite": "^6",
    "typescript": "^5",
    "tailwindcss": "^4",
    "@types/react": "^19"
  }
}
```

Only addition vs sales tracker: `react-router-dom` for two-page navigation.

## Deployment

### Render Setup

**Backend (Web Service)**:
- Root: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment: `SUPABASE_URL`, `SUPABASE_KEY`, `ANTHROPIC_API_KEY`

**Frontend (Static Site)**:
- Root: `frontend`
- Build: `npm install && npm run build`
- Publish: `dist`
- Environment: `VITE_API_URL`
- Rewrite rule: `/*` -> `/index.html` (for React Router)

### Supabase

Separate Supabase project from the sales tracker. Free tier supports both.

## Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| Supabase | Free (within free tier limits) |
| Render backend | Free (with spin-down) or $7 starter |
| Render frontend | Free (static site) |
| Claude API | ~$0.42/month (55 calls/day x 30 days x $0.00025/call) |
| yfinance | Free |
| **Total** | **$0.42 - $7.42/month** |

The Claude API cost is even lower than the sales tracker because:
- 11 fixed sectors vs. potentially hundreds of companies
- ~55 API calls/run vs. potentially hundreds
- Sector narrative generation is only 11 calls

## Environment Variables

```bash
# Backend
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
ANTHROPIC_API_KEY=sk-ant-...

# Frontend
VITE_API_URL=https://your-backend.onrender.com
```

## Development Workflow

```bash
# Clone and setup
git clone <repo>

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Seed database (first time)
# Run schema.sql then seed.sql in Supabase SQL Editor

# Run pipeline (fetch initial data)
curl -X POST http://localhost:8000/api/pipeline/run
```

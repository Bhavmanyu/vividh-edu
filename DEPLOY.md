# IndiaLens — Deployment Guide
## Total monthly cost: ₹0 (completely free)

## Stack
| Service | Provider | Cost |
|---------|----------|------|
| Frontend | Vercel Hobby | FREE |
| Backend API | Render Free | FREE |
| Database | Supabase Free | FREE |
| Scraping Cron | GitHub Actions | FREE |
| Email | Resend | FREE |
| Cache | Upstash Redis | FREE |

---

## Step 1: Supabase Database Setup

1. Go to https://supabase.com → New project
2. Note your project ref (e.g., `xyzabc123`)
3. Go to Settings → Database → Connection string → URI tab
4. Copy the **Transaction pooler** URI (port 6543):
   ```
   postgresql://postgres.PROJECTREF:PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```
5. Set this as your `DATABASE_URL` environment variable everywhere

### Run migrations on Supabase:
```bash
cd backend
export DATABASE_URL="postgresql://postgres.PROJECTREF:PASSWORD@..."
# Install sync psycopg2 for alembic
pip install psycopg2-binary
# Run migrations
alembic upgrade head
# Seed initial data
python -m scripts.seed_db
python -m scripts.seed_expanded
```

---

## Step 2: Render Backend Deployment

1. Push code to GitHub
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set root directory: `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1`
7. Plan: **Free**
8. Add environment variables (from your .env.example)

Or use the render.yaml file in backend/ — Render auto-detects it.

Note: Free Render services sleep after 15min of inactivity. 
Fix: The daily_cache_refresh GitHub Action pings the API every day keeping it warm.

### Get your API URL:
```
https://indialens-api.onrender.com
```

---

## Step 3: Vercel Frontend Deployment

```bash
cd indialens
npm install -g vercel
vercel login
vercel --prod
```

Or connect GitHub repo at https://vercel.com/new

### Required environment variables in Vercel:
```
NEXT_PUBLIC_API_URL=https://indialens-api.onrender.com
NEXT_PUBLIC_APP_URL=https://indialens.in
```

### Custom domain:
1. Vercel → Settings → Domains → Add `indialens.in`
2. Add CNAME record: `indialens.in` → `cname.vercel-dns.com`

---

## Step 4: GitHub Actions Secrets

Add these secrets at: GitHub repo → Settings → Secrets → Actions:
```
DATABASE_URL=postgresql://postgres.PROJECTREF:PASSWORD@...
REDDIT_CLIENT_ID=your_reddit_app_client_id
REDDIT_CLIENT_SECRET=your_reddit_app_client_secret  
API_KEY_ADMIN=your_admin_api_key
API_BASE_URL=https://indialens-api.onrender.com
```

---

## Step 5: Verify deployment
```bash
# Backend health
curl https://indialens-api.onrender.com/health

# Frontend
open https://indialens.in

# Test analysis
curl -X POST https://indialens-api.onrender.com/api/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{"budget_inr": 500000, "target_field": "engineering-cs", "risk_tolerance": "medium"}'
```

---

## Supabase Free Tier Limits
- 500MB database storage
- 2GB bandwidth/month  
- 50MB file storage
- Unlimited API requests
- Project pauses after 1 week of inactivity on free tier
  → Fix: Enable "No pause" at Settings → General → Pause settings

## Render Free Tier Limits
- 512MB RAM
- Shared CPU
- Sleeps after 15min inactivity (wakes in ~30s)
- 750 hours/month (enough for 24/7)
- No custom domains on free (use .onrender.com subdomain)
  → Upgrade to Render Starter ($7/mo) for custom domain + no sleep

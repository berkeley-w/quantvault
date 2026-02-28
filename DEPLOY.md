# Deploying QuantVault on Render

## Fix: Trader data (Blotter, Compliance, Securities, Audit Log) not loading

With **one** Render service, data loads only if the backend has the right environment variables and the service is awake. Do this:

### 1. Set required environment variables

In **Render Dashboard** → your **QuantVault** service → **Environment**:

| Key           | Required | What to set |
|----------------|----------|-------------|
| **JWT_SECRET** | Yes      | A long random string (e.g. 32+ characters). If you use the repo’s `render.yaml`, Render can auto-generate this. |
| **DATABASE_URL** | For persistent data | Your **Postgres** connection string. On Render: create a Postgres database, then in the service Environment add `DATABASE_URL` and paste the **Internal Database URL**. If you leave this unset, the app uses SQLite; on Render’s free tier the filesystem is ephemeral, so data may be lost on redeploy. |

Save and **redeploy** the service after changing env vars.

### 2. Use the right build and start commands

The repo includes a **render.yaml** so Render can use:

- **Build:** install Python deps, then build the frontend (`npm ci && npm run build` in `frontend/`).
- **Start:** `cd backend && python start.py` (uses `PORT` from Render).

If you already created the service by hand, set:

- **Build command:** `pip install -r backend/requirements.txt && cd frontend && npm ci && npm run build`
- **Start command:** `cd backend && python start.py`

### 3. Cold start (free tier)

On the free plan the service sleeps after inactivity. The first request after wake-up can take 30–60 seconds.

- After opening the app, wait up to a minute, then open Blotter or Securities again.
- Or use a paid plan so the service doesn’t sleep.

### 4. If data still doesn’t load

1. **Render → Logs**  
   Reproduce the issue (log in, open Blotter). Look for 500 errors or Python tracebacks.
2. **Browser → F12 → Network**  
   Open Blotter and check the request to `/api/v1/trades` (or similar):
   - **Pending then fail** → often cold start; wait longer or upgrade.
   - **401** → auth: ensure `JWT_SECRET` is set and you’re logged in again after changing it.
   - **500** → check Render logs; often DB or missing env.

---

## Two Render services (separate frontend and backend)

If the frontend is a **static site** (or separate service) and the API is another service:

1. In the **frontend** service Environment, set **`VITE_API_URL`** to your backend URL (e.g. `https://quantvault-api.onrender.com`, no trailing slash).
2. Redeploy the frontend so the build picks up `VITE_API_URL`.

---

## Local development

- Same origin: run backend and frontend as usual; leave `VITE_API_URL` unset.
- Point frontend at Render backend: in `frontend/.env.local` add  
  `VITE_API_URL=https://your-backend.onrender.com`

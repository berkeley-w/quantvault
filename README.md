# QuantVault - Platform Evolution

## Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Alpha Vantage API key (optional, for live price data)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment (if not already done):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional):**
   Create or update `.env` file in the `backend` directory:
   ```
   DATABASE_URL=sqlite:///./quantvault.db
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   JWT_SECRET=your-secret-key-change-in-production
   JWT_EXPIRY_HOURS=24
   ```

5. **Run database migrations:**
   Migrations will run automatically on startup, but you can also run manually:
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```bash
   python start.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies (if not already installed):**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

4. **For production build:**
   ```bash
   npm run build
   ```
   The built files will be in `frontend/dist/` and will be served by the backend when running in production mode.

### Running Both Together

**Option 1: Development Mode (Recommended)**
- Terminal 1: Run backend (`cd backend && python start.py`)
- Terminal 2: Run frontend (`cd frontend && npm run dev`)
- Access frontend at `http://localhost:5173` (Vite dev server proxies API calls)

**Option 2: Production Mode**
- Build frontend: `cd frontend && npm run build`
- Run backend: `cd backend && python start.py`
- Access everything at `http://localhost:8000` (backend serves the built frontend)

### First-Time Setup

1. When you first access the app, you'll see the login/setup page
2. Create the first admin user (this can only be done once)
3. After setup, you can log in with your admin credentials
4. The database will be automatically seeded with sample data on first run (if using `start.py`)

### API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Features

- **Authentication**: JWT-based auth with admin/trader roles
- **Trades**: Full CRUD with risk warnings
- **Holdings**: Materialized for performance
- **Technical Analysis**: SMA, EMA, RSI, MACD, Bollinger Bands, ATR
- **Signals**: Automated strategy-based signals
- **Risk Metrics**: VaR, Sharpe ratio, drawdown, concentration
- **WebSockets**: Live updates for trades, prices, and signals
- **Mobile Responsive**: Optimized for phone and tablet access

### Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (should be 3.11+)
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check database file permissions

**Frontend won't start:**
- Check Node version: `node --version` (should be 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

**API calls failing:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/config.py`
- Verify API routes are using `/api/v1/` prefix

**Database issues:**
- Migrations run automatically on startup
- To reset: delete `quantvault.db` and restart (will recreate schema)
- To manually run migrations: `alembic upgrade head`

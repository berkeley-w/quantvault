"""
Seed the QuantVault database with sample securities, traders, trades, and restricted list.
Run from backend directory: python seed.py
Uses init_db() to create tables.
"""
from models import init_db, SessionLocal, Security, Trader, Trade, RestrictedList

init_db()
db = SessionLocal()

# Sample securities (ticker universe with manual prices)
securities = [
    {"ticker": "AAPL", "name": "Apple Inc", "sector": "Technology", "price": 225.40, "shares_outstanding": 15_400_000_000},
    {"ticker": "MSFT", "name": "Microsoft Corp", "sector": "Technology", "price": 420.80, "shares_outstanding": 7_430_000_000},
    {"ticker": "NVDA", "name": "NVIDIA Corp", "sector": "Technology", "price": 880.50, "shares_outstanding": 24_500_000_000},
    {"ticker": "GOOGL", "name": "Alphabet Inc", "sector": "Technology", "price": 175.20, "shares_outstanding": 12_200_000_000},
    {"ticker": "AMZN", "name": "Amazon.com", "sector": "Consumer Disc", "price": 198.60, "shares_outstanding": 10_300_000_000},
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financials", "price": 218.40, "shares_outstanding": 2_870_000_000},
    {"ticker": "TSLA", "name": "Tesla Inc", "sector": "Consumer Disc", "price": 245.90, "shares_outstanding": 3_210_000_000},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer Staples", "price": 168.40, "shares_outstanding": 2_360_000_000},
    {"ticker": "GME", "name": "GameStop Corp", "sector": "Consumer Disc", "price": 28.50, "shares_outstanding": 305_000_000},
    {"ticker": "BABA", "name": "Alibaba Group", "sector": "Technology", "price": 72.00, "shares_outstanding": 2_500_000_000},
]
for s in securities:
    db.add(Security(**s))

# Sample traders
traders = [
    {"name": "Sarah Chen", "desk": "Asia Equities", "email": "sarah.chen@quantvault.com"},
    {"name": "James Mitchell", "desk": "US Large Cap", "email": "james.mitchell@quantvault.com"},
    {"name": "Elena Rodriguez", "desk": "EMEA Equities", "email": "elena.rodriguez@quantvault.com"},
]
for t in traders:
    db.add(Trader(**t))

db.commit()

# Resolve trader names for trades
trader_names = [t["name"] for t in traders]

# Sample trades (ACTIVE) - these will compute to initial holdings
trades = [
    {"ticker": "AAPL", "side": "BUY", "quantity": 1000, "price": 220.00, "trader_name": "Sarah Chen", "strategy": "Core", "notes": "Initial", "status": "ACTIVE"},
    {"ticker": "AAPL", "side": "BUY", "quantity": 500, "price": 225.00, "trader_name": "James Mitchell", "strategy": "Add", "notes": "", "status": "ACTIVE"},
    {"ticker": "MSFT", "side": "BUY", "quantity": 800, "price": 410.00, "trader_name": "Sarah Chen", "strategy": "Core", "notes": "", "status": "ACTIVE"},
    {"ticker": "NVDA", "side": "BUY", "quantity": 200, "price": 850.00, "trader_name": "James Mitchell", "strategy": "Tech", "notes": "", "status": "ACTIVE"},
    {"ticker": "JPM", "side": "BUY", "quantity": 1500, "price": 210.00, "trader_name": "Elena Rodriguez", "strategy": "Financials", "notes": "", "status": "ACTIVE"},
    {"ticker": "TSLA", "side": "BUY", "quantity": 300, "price": 240.00, "trader_name": "Sarah Chen", "strategy": "Momentum", "notes": "", "status": "ACTIVE"},
]
for t in trades:
    db.add(Trade(**t))

# One rejected trade for demo
db.add(Trade(
    ticker="PG",
    side="BUY",
    quantity=500,
    price=165.00,
    trader_name="James Mitchell",
    strategy="Staples",
    notes="Rejected sample",
    status="REJECTED",
    rejection_reason="Exceeded sector limit",
))

# Restricted list
restricted = [
    {"ticker": "GME", "reason": "Meme stock — excess retail-driven volatility", "added_by": "Compliance"},
    {"ticker": "BABA", "reason": "China regulatory & VIE structure uncertainty", "added_by": "Risk"},
]
for r in restricted:
    db.add(RestrictedList(**r))

db.commit()
db.close()
print("Database seeded: securities, traders, trades, restricted list.")

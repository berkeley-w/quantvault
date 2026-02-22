"""
Seed the QuantVault database with sample data. 
Run directly or import and call seed_data().
Checks if already seeded to avoid duplicate data on repeated seeding.
"""
from models import init_db, SessionLocal, Security, Trader, Trade, RestrictedList

def seed_data():
    init_db()
    db = SessionLocal()
    try:
        # Check if any Security rows exist (already seeded)
        if db.query(Security).first():
            print("Database already seeded. No action taken.")
            db.close()
            return

        # Sample securities (across various sectors)
        securities = [
            {"ticker": "AAPL", "name": "Apple Inc", "sector": "Technology", "price": 225.40, "shares_outstanding": 15_400_000_000},
            {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financials", "price": 218.40, "shares_outstanding": 2_870_000_000},
            {"ticker": "CVX", "name": "Chevron Corp", "sector": "Energy", "price": 158.60, "shares_outstanding": 1_900_000_000},
            {"ticker": "PFE", "name": "Pfizer Inc", "sector": "Healthcare", "price": 32.90, "shares_outstanding": 5_630_000_000},
            {"ticker": "MSFT", "name": "Microsoft Corp", "sector": "Technology", "price": 420.80, "shares_outstanding": 7_430_000_000},
            {"ticker": "TSLA", "name": "Tesla Inc", "sector": "Consumer Disc", "price": 245.90, "shares_outstanding": 3_210_000_000},
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

        db.commit()  # Commit so foreign keys, etc. are available

        # Sample trades (ACTIVE)
        trades = [
            {"ticker": "AAPL", "side": "BUY", "quantity": 1000, "price": 220.00, "trader_name": "Sarah Chen", "strategy": "Core", "notes": "Initial", "status": "ACTIVE"},
            {"ticker": "MSFT", "side": "BUY", "quantity": 500, "price": 415.00, "trader_name": "James Mitchell", "strategy": "Growth", "notes": "", "status": "ACTIVE"},
            {"ticker": "JPM", "side": "BUY", "quantity": 800, "price": 210.50, "trader_name": "Elena Rodriguez", "strategy": "Yield", "notes": "", "status": "ACTIVE"},
            {"ticker": "CVX", "side": "BUY", "quantity": 300, "price": 152.20, "trader_name": "Sarah Chen", "strategy": "Energy Play", "notes": "", "status": "ACTIVE"},
            {"ticker": "PFE", "side": "BUY", "quantity": 1200, "price": 30.20, "trader_name": "James Mitchell", "strategy": "Healthcare", "notes": "", "status": "ACTIVE"},
        ]
        for t in trades:
            db.add(Trade(**t))

        # One rejected trade for demo
        db.add(Trade(
            ticker="TSLA",
            side="BUY",
            quantity=500,
            price=240.00,
            trader_name="Elena Rodriguez",
            strategy="Momentum",
            notes="Sample rejected trade",
            status="REJECTED",
            rejection_reason="Exceeded risk limit",
        ))

        # Restricted list (just one, as required)
        restricted = [
            {"ticker": "CVX", "reason": "Under investigation for compliance breach", "added_by": "Compliance"},
        ]
        for r in restricted:
            db.add(RestrictedList(**r))

        db.commit()
        print("Database seeded: securities, traders, trades, restricted list.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

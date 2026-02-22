from typing import List, Dict

NAV = 250_000_000  # Fund NAV in dollars
MAX_GROSS_EXP = 1.5  # 150%
SHAREHOLDING_LIMIT_CRITICAL = 0.30  # 30%
SHAREHOLDING_LIMIT_WARNING = 0.10   # 10%

def compliance_check(
    ticker: str,
    side: str,
    qty: float,
    price: float,
    holdings: List[Dict]
) -> List[Dict]:
    """
    Compliance checks for order placement.
    Args:
        ticker (str): Security ticker
        side (str): 'buy' or 'sell'
        qty (float): Number of shares to trade
        price (float): Trade price per share
        holdings (List[Dict]): List of holding dicts, each includes
            ['ticker', 'shares', 'shares_outstanding']
    Returns:
        List[Dict]: [{severity: "critical"|"warn", code: str, message: str}, ...]
    """
    flags = []
    side = side.lower()
    # Lookup current holding for ticker
    holding = next((h for h in holdings if h['ticker'] == ticker), None)
    shares_held = holding['shares'] if holding else 0
    shares_outstanding = holding['shares_outstanding'] if holding and holding['shares_outstanding'] else None

    # Rule 1: No short selling
    if side == "sell":
        if qty > shares_held:
            flags.append({
                "severity": "critical",
                "code": "NO_SHORT",
                "message": f"Attempting to sell {qty} shares of {ticker} but only {shares_held} held — short selling is not allowed."
            })

    # Compute new holdings post-trade for this ticker
    shares_new = shares_held + qty if side == "buy" else shares_held - qty

    # Rule 2: Shareholding limits
    if shares_outstanding and shares_outstanding > 0:
        pct = shares_new / shares_outstanding
        if pct > SHAREHOLDING_LIMIT_CRITICAL:
            flags.append({
                "severity": "critical",
                "code": "SHAREHOLDING_LIMIT",
                "message": f"Order will result in holding {pct*100:.4f}% of {ticker} shares outstanding (limit: 30%)."
            })
        elif pct > SHAREHOLDING_LIMIT_WARNING:
            flags.append({
                "severity": "warn",
                "code": "SHAREHOLDING_WARN",
                "message": f"Order will result in holding {pct*100:.4f}% of {ticker} shares outstanding (soft warning at 10%)."
            })

    # Rule 3: Gross exposure limit

    # Sum gross notional exposure including this trade
    gross_exposure = 0.0
    for h in holdings:
        # Use latest price for target ticker, else use holding's price or skip if unavailable
        if h['ticker'] == ticker:
            gross_exposure += abs(shares_new * price)
        else:
            px = h.get('current_price') or h.get('avg_cost') or 0
            gross_exposure += abs(h['shares'] * px)
    # If the ticker was not in holdings, add the new position
    if not holding:
        gross_exposure += abs(qty * price)

    gross_exp_pct = gross_exposure / NAV

    if gross_exp_pct > MAX_GROSS_EXP:
        flags.append({
            "severity": "critical",
            "code": "GROSS_EXPOSURE",
            "message": f"Gross exposure after trade: ${gross_exposure:,.0f} ({gross_exp_pct*100:.2f}% of NAV), above the 150% limit."
        })

    return flags
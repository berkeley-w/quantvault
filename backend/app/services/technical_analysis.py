"""
Technical Analysis Service

Pure functions that compute technical indicators from OHLCV arrays.
No database dependencies - receives arrays and returns arrays.
"""
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def sma(prices: List[float], period: int) -> List[float | None]:
    """
    Simple Moving Average.
    Returns array of same length as input, with None for first (period-1) values.
    """
    if len(prices) < period:
        return [None] * len(prices)

    result: List[float | None] = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1 : i + 1]
        avg = sum(window) / period
        result.append(avg)
    return result


def ema(prices: List[float], period: int) -> List[float | None]:
    """
    Exponential Moving Average.
    Uses standard EMA formula: EMA = (Price - EMA_prev) * (2 / (period + 1)) + EMA_prev
    """
    if len(prices) < period:
        return [None] * len(prices)

    result: List[float | None] = [None] * (period - 1)
    multiplier = 2.0 / (period + 1)

    # Initialize with SMA of first period values
    initial_sma = sum(prices[:period]) / period
    result.append(initial_sma)
    ema_prev = initial_sma

    for i in range(period, len(prices)):
        ema_current = (prices[i] - ema_prev) * multiplier + ema_prev
        result.append(ema_current)
        ema_prev = ema_current

    return result


def rsi(prices: List[float], period: int = 14) -> List[float | None]:
    """
    Relative Strength Index.
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss over period
    """
    if len(prices) < period + 1:
        return [None] * len(prices)

    result: List[float | None] = [None] * period

    # Calculate price changes
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

    # Calculate initial average gain and loss
    gains = [c if c > 0 else 0.0 for c in changes[:period]]
    losses = [-c if c < 0 else 0.0 for c in changes[:period]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_value = 100.0 - (100.0 / (1.0 + rs))
        result.append(rsi_value)

    # Calculate subsequent RSI values using Wilder's smoothing
    for i in range(period, len(changes)):
        change = changes[i]
        gain = change if change > 0 else 0.0
        loss = -change if change < 0 else 0.0

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_value = 100.0 - (100.0 / (1.0 + rs))
            result.append(rsi_value)

    return result


def macd(
    prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
) -> Tuple[List[float | None], List[float | None], List[float | None]]:
    """
    Moving Average Convergence Divergence.
    Returns (MACD line, Signal line, Histogram) as three arrays.
    """
    ema_fast = ema(prices, fast_period)
    ema_slow = ema(prices, slow_period)

    # MACD line = EMA(fast) - EMA(slow)
    macd_line: List[float | None] = []
    for i in range(len(prices)):
        if ema_fast[i] is None or ema_slow[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(ema_fast[i] - ema_slow[i])

    # Signal line = EMA of MACD line
    # Filter out None values for EMA calculation
    macd_values = [v for v in macd_line if v is not None]
    if len(macd_values) < signal_period:
        signal_line = [None] * len(macd_line)
    else:
        signal_line_raw = ema(macd_values, signal_period)
        # Map back to original positions
        signal_line = [None] * len(macd_line)
        signal_idx = 0
        for i in range(len(macd_line)):
            if macd_line[i] is not None:
                if signal_idx < len(signal_line_raw):
                    signal_line[i] = signal_line_raw[signal_idx]
                signal_idx += 1

    # Histogram = MACD - Signal
    histogram: List[float | None] = []
    for i in range(len(macd_line)):
        if macd_line[i] is None or signal_line[i] is None:
            histogram.append(None)
        else:
            histogram.append(macd_line[i] - signal_line[i])

    return (macd_line, signal_line, histogram)


def bollinger_bands(
    prices: List[float], period: int = 20, num_std: float = 2.0
) -> Tuple[List[float | None], List[float | None], List[float | None]]:
    """
    Bollinger Bands.
    Returns (Upper band, Middle band (SMA), Lower band) as three arrays.
    """
    sma_values = sma(prices, period)
    result_upper: List[float | None] = []
    result_middle: List[float | None] = sma_values
    result_lower: List[float | None] = []

    for i in range(len(prices)):
        if sma_values[i] is None:
            result_upper.append(None)
            result_lower.append(None)
        else:
            # Calculate standard deviation of the window
            start_idx = i - period + 1
            window = prices[start_idx : i + 1]
            mean = sma_values[i]
            variance = sum((p - mean) ** 2 for p in window) / period
            std_dev = variance ** 0.5

            upper = mean + (num_std * std_dev)
            lower = mean - (num_std * std_dev)
            result_upper.append(upper)
            result_lower.append(lower)

    return (result_upper, result_middle, result_lower)


def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float | None]:
    """
    Average True Range.
    True Range = max(high - low, abs(high - prev_close), abs(low - prev_close))
    ATR = SMA of True Range
    """
    if len(highs) != len(lows) or len(highs) != len(closes) or len(highs) < period + 1:
        return [None] * len(highs)

    true_ranges: List[float] = []

    for i in range(1, len(highs)):
        tr1 = highs[i] - lows[i]
        tr2 = abs(highs[i] - closes[i - 1])
        tr3 = abs(lows[i] - closes[i - 1])
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)

    # Calculate ATR as SMA of True Range
    atr_values = sma(true_ranges, period)
    # Pad with None at the beginning to match input length
    return [None] + atr_values

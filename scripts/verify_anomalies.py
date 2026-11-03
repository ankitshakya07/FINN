import sys
sys.path.insert(0, "backend")
from app.db import connect
from app.prices import calculate_anomalies

with connect() as conn:
    rows = [dict(r) for r in conn.execute("SELECT trading_date, close, volume FROM prices WHERE ticker='RELIANCE' ORDER BY trading_date ASC").fetchall()]

print("Total RELIANCE sessions:", len(rows))
latest = rows[-1]
prev = rows[-2]
prior_20 = rows[-21:-1]
avg_vol_20d = sum(r['volume'] for r in prior_20) / 20.0
latest_vol = latest['volume']
vol_ratio = latest_vol / avg_vol_20d
change_pct = ((latest['close'] - prev['close']) / prev['close']) * 100.0

print(f"Latest date: {latest['trading_date']}, Close: {latest['close']}, Volume: {latest_vol}")
print(f"Prev date: {prev['trading_date']}, Close: {prev['close']}, Volume: {prev['volume']}")
print(f"20d Prior Avg Volume: {avg_vol_20d:.2f}")
print(f"Hand-calculated vol multiple: {vol_ratio:.4f}x")
print(f"Hand-calculated change %: {change_pct:+.4f}%")

anoms = calculate_anomalies("RELIANCE", rows, vol_x=1.0, pct=0.5)
print("Detected anomalies count at vol_x=1.0, pct=0.5:", len(anoms))
for a in anoms:
    print(" ", a)


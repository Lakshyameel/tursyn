import pandas as pd
import numpy as np
import re
from sklearn.linear_model import LinearRegression

# =====================================
# 🔮 1. REVENUE FORECASTING
# =====================================
def forecast_revenue(df):
    if df.empty or len(df["Timestamp"].dt.date.unique()) < 2:
        return pd.DataFrame()

    df["Date"] = df["Timestamp"].dt.date
    daily = df.groupby("Date")["Total"].sum().reset_index()

    # Using Linear Regression to find the trend line
    daily["DayIndex"] = np.arange(len(daily))
    X = daily[["DayIndex"]]
    y = daily["Total"]

    model = LinearRegression()
    model.fit(X, y)

    # Predict for the next 7 days
    future_indices = np.arange(len(daily), len(daily) + 7).reshape(-1, 1)
    predictions = model.predict(future_indices)

    future_dates = pd.date_range(
        start=pd.to_datetime(daily["Date"].iloc[-1]) + pd.Timedelta(days=1),
        periods=7
    )

    return pd.DataFrame({
        "Date": future_dates,
        "Predicted Revenue": np.maximum(predictions, 0)
    })

# =====================================
# 🚨 2. ANOMALY DETECTION
# =====================================
def detect_revenue_anomaly(df):
    if df.empty:
        return None
    
    df["Date"] = df["Timestamp"].dt.date
    daily = df.groupby("Date")["Total"].sum().reset_index()
    
    if len(daily) < 3:
        return None
        
    mean = daily["Total"].mean()
    std = daily["Total"].std()
    
    if std == 0: return None

    # Identify days where revenue is beyond 2 standard deviations from the mean
    # This captures both extreme surges and unexpected drops
    anomalies = daily[(daily["Total"] > mean + 2 * std) | (daily["Total"] < mean - 2 * std)]
    return anomalies

# =====================================
# ⚠️ 3. BUSINESS ALERTS
# =====================================
def generate_business_alerts(df):
    alerts = []
    if df.empty:
        return alerts

    # Alert 1: Sharp Decline Check
    df["Date"] = df["Timestamp"].dt.date
    daily = df.groupby("Date")["Total"].sum()
    if len(daily) >= 2:
        last_day = daily.iloc[-1]
        prev_day = daily.iloc[-2]
        if last_day < prev_day * 0.5:
            alerts.append(f"⚠️ Revenue Alert: Sales dropped by {100 - (last_day/prev_day*100):.1f}% since yesterday!")

    # Alert 2: Dependency Check (Risk Mitigation)
    item_list = [re.sub(r'\d+', '', i).strip().lower() for items in df["Items"] for i in items.split(",")]
    if item_list:
        counts = pd.Series(item_list).value_counts()
        top_item_share = (counts.max() / len(item_list)) * 100
        if top_item_share > 60:
            alerts.append(f"⚠️ Diversity Alert: {counts.idxmax().capitalize()} accounts for {top_item_share:.1f}% of sales. High risk if this item becomes unavailable!")

    return alerts

# =====================================
# 📊 4. TREND INTELLIGENCE
# =====================================
def detect_item_trends(df):
    if df.empty:
        return None, None, 0

    item_data = []
    for _, row in df.iterrows():
        items = row["Items"].split(",")
        for item in items:
            name = re.sub(r'\d+', '', item).strip().lower()
            item_data.append([row["Timestamp"].date(), name])

    item_df = pd.DataFrame(item_data, columns=["Date", "Item"])
    counts = item_df["Item"].value_counts()
    
    if counts.empty:
        return None, None, 0

    return counts.idxmax(), counts.idxmin(), round((counts.max() / len(item_df)) * 100, 1)

# =====================================
# 🚀 5. DEMAND PREDICTION
# =====================================
def predict_top_item(df):
    if df.empty:
        return None, 0
    
    item_list = []
    for items in df["Items"]:
        for itm in items.split(","):
            qty = int(re.search(r'\d+', itm).group()) if re.search(r'\d+', itm) else 1
            name = re.sub(r'\d+', '', itm).strip().lower()
            item_list.append({"Item": name, "Qty": qty})

    item_df = pd.DataFrame(item_list)
    item_stats = item_df.groupby("Item")["Qty"].sum()
    num_days = len(df["Timestamp"].dt.date.unique())
    
    # Predict based on average daily volume of the top seller
    return item_stats.idxmax(), int(np.ceil(item_stats.max() / num_days))

# =====================================
# 💰 6. PROFIT INTELLIGENCE
# =====================================
def calculate_profit(df, menu):
    """
    Calculates total profit per item.
    Handles case-insensitive matching and capitalized dictionary keys.
    """
    if df.empty:
        return pd.Series(dtype=float)

    # 1. Parse item quantities from order strings
    item_list = []
    for items in df["Items"]:
        for itm in items.split(","):
            qty = int(re.search(r'\d+', itm).group()) if re.search(r'\d+', itm) else 1
            name = re.sub(r'\d+', '', itm).strip().lower()
            item_list.append({"Item": name, "Qty": qty})

    item_df = pd.DataFrame(item_list)
    total_qty = item_df.groupby("Item")["Qty"].sum()

    # 2. Calculate profit using margins
    profits = {}
    for item_name, qty in total_qty.items():
        # Case-insensitive lookup in the menu dictionary
        match = next((m for m in menu if m.lower() == item_name), None)
        
        if match:
            # Check for both lowercase and capitalized keys
            price = menu[match].get("Price") or menu[match].get("price", 0)
            cost = menu[match].get("Cost") or menu[match].get("cost", 0)
            
            profit_per_unit = price - cost
            profits[match.capitalize()] = qty * profit_per_unit
        else:
            profits[item_name.capitalize()] = 0

    return pd.Series(profits, name="Profit")
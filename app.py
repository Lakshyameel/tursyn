import streamlit as st
import pandas as pd
import re
import time
from collections import Counter
from itertools import combinations
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# =====================================
# 🎨 CUSTOM STYLES (Glassmorphism)
# =====================================

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a, #020617);
        color: white;
    }

    /* Glass Container */
    .glass {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
    }

    /* Status Indicators */
    .status-active { color: #10b981; font-weight: bold; }
    .status-idle { color: #64748b; }
    
    /* Metrics override for dark mode */
    [data-testid="stMetricValue"] { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================
# 🚀 FOUNDATION & SESSION STATE
# =====================================

st.set_page_config(page_title="AI Restaurant Dashboard", layout="wide")

try:
    from database import get_all_orders, save_order, create_orders_table
    from analytics import (
        forecast_revenue, detect_revenue_anomaly, 
        generate_business_alerts, detect_item_trends, calculate_profit
    )
    from order_engine import process_order
except ImportError:
    st.error("Missing local modules. Ensure database.py and analytics.py are in the folder.")
    st.stop()

create_orders_table()

if "restaurant" not in st.session_state:
    st.session_state.restaurant = "demo"
if "pending_order" not in st.session_state:
    st.session_state.pending_order = None
if "show_payment" not in st.session_state:
    st.session_state.show_payment = False

# Sidebar
st.sidebar.title("📌 Navigation")
st.sidebar.text_input("Customer ID / Name", value="guest", key="customer_id")
st.sidebar.text_input("Restaurant Name", key="restaurant")
page = st.sidebar.radio("Go to", ["Dashboard", "Place Order", "View Orders"])

# =====================================
# 🛠️ HELPERS & DATA LOADING
# =====================================

def generate_recommendations(df):
    if df.empty: return []
    all_pairs = []
    for items in df["Items"]:
        if isinstance(items, str):
            split_items = [re.sub(r'\d+', '', x).strip().lower() for x in items.split(",")]
            all_pairs.extend(combinations(split_items, 2))
    return Counter(all_pairs).most_common(3)

@st.cache_data
def load_menu():
    try: return pd.read_csv("data/menu.csv")
    except: return pd.DataFrame(columns=["Item", "Price"])

@st.cache_data
def load_orders():
    orders = get_all_orders()
    if orders:
        df = pd.DataFrame(orders, columns=[
            "OrderID", "RestaurantID", "CustomerID", "Items", 
            "Quantities", "Total", "Timestamp", "Source"
        ])
        df["Total"] = pd.to_numeric(df["Total"], errors='coerce').fillna(0)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        return df
    return pd.DataFrame(columns=["OrderID", "RestaurantID", "CustomerID", "Items", "Quantities", "Total", "Timestamp", "Source"])

menu = load_menu()
df = load_orders()
if not df.empty and "RestaurantID" in df.columns:
    df = df[df["RestaurantID"] == st.session_state.restaurant]

# =====================================
# 📊 DASHBOARD (Steps 2 & 3)
# =====================================
if page == "Dashboard":
    st.title(f"📊 Business Dashboard: {st.session_state.restaurant}")
    
    if df.empty:
        st.warning("No orders found for this location.")
    else:
        # ⭐ STEP 2: Wrap Dashboard Cards in Glass
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Revenue", f"₹{df['Total'].sum():.2f}")
        m2.metric("📦 Total Orders", len(df))
        m3.metric("📊 Avg Order Value", f"₹{df['Total'].mean():.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("📈 Revenue Over Time")
        df["Date"] = df["Timestamp"].dt.date
        st.line_chart(df.groupby("Date")["Total"].sum())

        # ⭐ STEP 3: Upgrade Insight Section with Glass
        st.header("🤖 AI Business Insights")
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        
        with col_a:
            recs = generate_recommendations(df)
            st.subheader("💡 Smart Upsells")
            if recs:
                for pair, count in recs:
                    st.info(f"Top Pair: **{pair[0].title()}** + **{pair[1].title()}**")
            else: st.write("Collecting data...")

        with col_b:
            if "Source" in df.columns:
                st.subheader("🎤 Channel Split")
                st.bar_chart(df["Source"].value_counts())
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================
# 🛒 PLACE ORDER (Step 4)
# =====================================
elif page == "Place Order":
    st.title("🛒 AI Ordering System")
    st.subheader("📜 Current Menu")
    st.dataframe(menu, use_container_width=True)

    if not st.session_state.show_payment:
        # --- ⌨️ KEYBOARD ENTRY ---
        st.subheader("⌨️ Keyboard Entry")
        order_input = st.text_input("Enter order", key="manual_in")
        if st.button("Process Order"):
            if order_input:
                from voice_order_parser import parse_voice_order
                items, total = process_order(parse_voice_order(order_input), menu)
                if total > 0:
                    st.session_state.pending_order = (items, total, "text")
                    st.rerun()

        # --- 🎤 VOICE ENTRY (Line 173 Fix) ---
        st.subheader("🎤 Voice Entry")
        webrtc_ctx = webrtc_streamer(
            key="mic", 
            mode=WebRtcMode.SENDONLY,
            media_stream_constraints={"audio": True, "video": False},
            # ✅ Fixed: Buffer size to prevent Queue Overflow
            audio_receiver_size=1024,
            async_processing=True
        )

        # 🧠 Logic: Status Indicator
        if webrtc_ctx.state.playing:
            st.markdown('Status: <span class="status-active">● LISTENING</span>', unsafe_allow_html=True)
        else:
            st.markdown('Status: <span class="status-idle">○ IDLE (Press Start)</span>', unsafe_allow_html=True)

        if webrtc_ctx.audio_receiver:
            audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            
            # ✅ Debug Checklist
            if audio_frames:
                st.write(f"✅ Debug: Frames received: **{len(audio_frames)}**")
                
                try:
                    from voice_browser_stt import transcribe_audio
                    from llm_order_extractor import llm_extract_order
                    
                    with st.spinner("AI is thinking..."):
                        # ✅ Logic: Pass the frames list directly to your WAV helper
                        text = transcribe_audio(audio_frames)
                        
                        if text:
                            st.write(f"Recognized: *{text}*")
                            menu_list = menu["Item"].str.lower().tolist()
                            order_json = llm_extract_order(text, menu_list)
                            items, total = process_order(order_json, menu)
                            
                            if total > 0:
                                st.session_state.pending_order = (items, total, "voice")
                                st.rerun()
                        else:
                            st.error("❌ Debug: No text returned. Check STT format.")
                except Exception as e:
                    st.error(f"Voice Error: {e}")
            else:
                st.warning("⚠️ Debug: 0 frames received. Check mic permissions.")

    # --- 📝 REVIEW & PAYMENT BLOCKS ---
    if st.session_state.pending_order and not st.session_state.show_payment:
        items, total, source = st.session_state.pending_order
        st.divider()
        st.subheader(f"📝 Review {source.title()} Order")
        st.success(f"**Items:** {items}  \n**Total:** ₹{total:.2f}")
        
        # 🥤 Simple Upsell
        if "pizza" in items.lower() and "pepsi" not in items.lower():
            if st.button("✅ Add Pepsi (Combo Offer)"):
                pepsi_price = menu[menu["Item"].str.lower()=="pepsi"]["Price"].iloc[0]
                st.session_state.pending_order = (items + ", 1 pepsi", total + pepsi_price, source)
                st.rerun()

        if st.button("✅ Confirm & Save"):
            save_order(st.session_state.restaurant, st.session_state.get("customer_id", "guest"), items, "N/A", total, source)
            st.session_state.show_payment = True
            st.rerun()
        
        if st.button("❌ Start Over"):
            st.session_state.pending_order = None
            st.rerun()

    if st.session_state.show_payment:
        st.divider()
        st.subheader("💳 Secure Payment")
        if st.button("🚀 Complete Payment"):
            st.balloons()
            time.sleep(2)
            st.session_state.pending_order = None
            st.session_state.show_payment = False
            st.cache_data.clear()
            st.rerun()

elif page == "View Orders":
    st.title("📋 Order History")
    history_df = load_orders()
    if not history_df.empty:
        history_df = history_df[history_df["RestaurantID"] == st.session_state.restaurant]
        st.dataframe(history_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
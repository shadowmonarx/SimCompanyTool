import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from pytz import UTC 
# === Constants ===
EXCHANGE_FEE_PERCENT = 4.0
MARKET_KIND = 16  # e.g., Silicon

# === Page Setup ===
st.set_page_config(page_title="Sim Profit Optimizer", layout="centered")
st.title("📈 SimCompanies Exchange Profit Optimizer")

st.markdown("""


> 📦 Compare Contract vs Exchange  
> 📉 Check your market ranking  
> 💡 Get price suggestions  
""")

st.markdown("---")
st.markdown("### 📥 Enter Listing Information")

# === Input Section ===
col1, col2 = st.columns(2)
with col1:
    quantity = st.number_input("🔢 Quantity", min_value=1, value=50000)
    contract_price = st.number_input("🤝 Contract Price ($)", min_value=0.0, value=9.30)
    your_price = st.number_input("🏷️ Your Exchange Price ($)", min_value=0.0, value=9.70)
   

with col2:
    transport_cost = st.number_input("🚚 Transport Cost / Unit ($)", min_value=0.0, value=0.49)
    source_cost = st.number_input("🏭 Production Cost / Unit ($)", min_value=0.0, value=5.00)
    quality = st.selectbox("🎖️ Product Quality", list(range(13)), index=0)


st.markdown("---")
st.markdown("### 💰 Profit Calculation Summary")

# === Contract Profit ===
contract_revenue = quantity * contract_price
contract_transport = (quantity / 2) * transport_cost
contract_cost = quantity * source_cost
contract_net = contract_revenue - contract_transport - contract_cost
contract_unit_profit = contract_net / quantity

# === Break-Even Exchange Price ===
required_exchange_price = (contract_unit_profit + transport_cost + source_cost) / (1 - EXCHANGE_FEE_PERCENT / 100)

# === Exchange Profit ===
exchange_revenue = quantity * your_price
exchange_transport = quantity * transport_cost
exchange_fee = exchange_revenue * EXCHANGE_FEE_PERCENT / 100
exchange_cost = quantity * source_cost
exchange_net = exchange_revenue - exchange_transport - exchange_fee - exchange_cost
exchange_unit_profit = exchange_net / quantity

# Calculate in-hand values (Revenue - other costs excluding production)
exchange_in_hand = exchange_revenue - exchange_transport - exchange_fee
contract_in_hand = contract_revenue - contract_transport

# Calculate in-hand money
contract_in_hand = contract_revenue - contract_transport
exchange_in_hand = exchange_revenue - exchange_transport - exchange_fee
in_hand_diff = exchange_in_hand - contract_in_hand


col3, col4 = st.columns(2)

with col3:
    st.metric("📈 Contract Profit/Unit", f"${contract_unit_profit:.4f}")
    st.metric("💰 Total Contract Profit", f"${contract_net:,.2f}")
    st.metric("🪙 Contract In-Hand (After Transport)", f"${contract_in_hand:,.2f}")
    st.markdown(" ")

with col4:
    st.metric("💹 Exchange Profit/Unit", f"${exchange_unit_profit:.4f}")
    st.metric("💰 Total Exchange Profit", f"${exchange_net:,.2f}")
    st.metric("🪙 Exchange In-Hand (After Cuts)", f"${exchange_in_hand:,.2f}")
    
st.markdown(f"<div style='font-size: 16px; padding-top: 0.5em;'>"
                f"📊 <b>In-Hand Difference:</b> <span style='color:{'green' if in_hand_diff >= 0 else 'red'}'>"
                f"${in_hand_diff:,.2f}</span></div>", unsafe_allow_html=True)

# === Market Fetch ===
@st.cache_data(ttl=300)
def fetch_market():
    try:
        url = f"https://www.simcompanies.com/api/v3/market/0/{MARKET_KIND}/"
        res = requests.get(url)
        df = pd.json_normalize(res.json())
        df['posted'] = pd.to_datetime(df['posted'], utc=True)
        return df
    except:
        return pd.DataFrame([])

market_df = fetch_market()
market_df = market_df[market_df['quality'] >= quality].copy()

# === Insert User Listing ===
user_listing = pd.DataFrame([{
    'price': your_price,
    'quality': quality,
    'quantity': quantity,
    'seller.company': 'Your Listing',
    'posted': datetime.now(UTC) - timedelta(minutes=1)
}])
combined_df = pd.concat([market_df, user_listing], ignore_index=True)

# === Real Sort Logic: Ascending Price, Desc Quality, Asc Time ===
def custom_sort_key(row):
    return (row['price'], -row['quality'], row['posted'])

combined_df['sort_key'] = combined_df.apply(custom_sort_key, axis=1)
combined_df = combined_df.sort_values(by='sort_key').drop(columns='sort_key').reset_index(drop=True)

# === Rank & Suggest Price ===
user_index = combined_df[
    (combined_df['price'] == your_price) &
    (combined_df['quality'] == quality) &
    (combined_df['quantity'] == quantity) &
    (combined_df['seller.company'] == 'Your Listing')
].index[0]

lowest_price = combined_df.iloc[0]['price']
smart_price = max(required_exchange_price, lowest_price - 0.01)

st.markdown("---")
st.markdown("### 📊 Verdict")
if your_price >= required_exchange_price:
    st.success("✅ Your listing beats contract profit.")
else:
    st.error("❌ Your listing underperforms vs contract.")

st.info(f"📌 Your listing ranks **#{user_index + 1} out of {len(combined_df)}**")
st.markdown(f"💡 Suggested Price to Compete: **${smart_price:.2f}**")

# === Market Table ===
with st.expander("📈 View Exchange Listings (Sorted)"):
    highlight_index = user_index  # for clarity
    display_df = combined_df[['price', 'quality', 'quantity', 'seller.company']].rename(columns={
        'price': 'Price ($)',
        'quality': 'Q',
        'quantity': 'Qty',
        'seller.company': 'Seller'
    })

    # Apply row highlight styling only (no extra column)
    styled_df = display_df.style.apply(
        lambda row: ['background-color: #ff3f3f' if row.name == highlight_index else '' for _ in row],
        axis=1
    )
    st.dataframe(styled_df)

# === Breakdown Table ===
with st.expander("📋 Full Breakdown: Contract vs Exchange"):
    table = pd.DataFrame({
        "Metric": ["Revenue", "Transport", "Production", "Exchange Fee", "Net Profit"],
        "Exchange": [
            f"${exchange_revenue:,.2f}",
            f"${exchange_transport:,.2f}",
            f"${exchange_cost:,.2f}",
            f"${exchange_fee:,.2f}",
            f"${exchange_net:,.2f}"
        ],
        "Contract": [
            f"${contract_revenue:,.2f}",
            f"${contract_transport:,.2f}",
            f"${contract_cost:,.2f}",
            "—",
            f"${contract_net:,.2f}"
        ]
    })
    st.table(table)

# === Footer ===
st.markdown("---")
st.markdown('[Made by **NOXUS TRADER**](https://www.simcompanies.com/company/0/Noxus-Trader/)', unsafe_allow_html=True)


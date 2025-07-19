import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="SimCompanies Profit Optimizer", layout="centered")
st.title("💹 SimCompanies Exchange Profit Optimizer")
st.markdown(
    "Use this tool to calculate the **minimum exchange price** required to beat contract profits — factoring in transport, exchange fees, and production costs."
)

# === Input Section with Card UI ===
st.markdown("---")

with st.container():

    st.markdown("#### Enter Your Scenario")

    col1, col2 = st.columns([1, 1])

    with col1:
        quantity = st.number_input(
            " Quantity of Product",
            min_value=1,
            value=167779,
            help="Total units you're planning to sell"
        )

        contract_price = st.number_input(
            "Contract Price Offered per Unit ($)",
            min_value=0.0,
            value=9.02,
            format="%.2f",
            help="Price you're offering to the buyer per unit via contract"
        )

        your_exchange_price = st.number_input(
            " Intended Exchange Price per Unit ($)",
            min_value=0.0,
            value=9.50,
            format="%.2f",
            help="Your target sale price on the exchange"
        )

    with col2:
        transport_cost = st.number_input(
            " Transport Cost per Unit ($)",
            min_value=0.0,
            value=0.49,
            format="%.2f",
            help="How much it costs to transport 1 unit"
        )

        source_cost = st.number_input(
            " Source Cost per Unit ($)",
            min_value=0.0,
            value=5.0,
            format="%.2f",
            help="How much it cost to produce 1 unit of this product"
        )

        exchange_fee_percent = 4.0  # Fixed
        st.markdown("💸 **Exchange Fee:** 4% (fixed)")

    st.markdown("</div>", unsafe_allow_html=True)

# === Calculations ===

# Contract Profit
contract_revenue = quantity * contract_price
contract_transport_cost = (quantity / 2) * transport_cost
contract_cost = quantity * source_cost
contract_net_profit_total = contract_revenue - contract_transport_cost - contract_cost
contract_net_profit_per_unit = contract_net_profit_total / quantity

# Required Exchange Price to Beat Contract (net profit basis)
required_exchange_price = (contract_net_profit_per_unit + transport_cost + source_cost) / (1 - exchange_fee_percent / 100)

# Exchange Profit
exchange_revenue = quantity * your_exchange_price
exchange_transport_cost = quantity * transport_cost
exchange_fee = exchange_revenue * (exchange_fee_percent / 100)
exchange_cost = quantity * source_cost
exchange_net_profit = exchange_revenue - exchange_transport_cost - exchange_fee - exchange_cost
exchange_net_profit_per_unit = exchange_net_profit / quantity

# === Results Summary ===
st.header(" Results Summary")

col3, col4 = st.columns(2)

with col3:
    st.markdown(f"**Contract Profit :** ${contract_net_profit_per_unit:.4f}")
    st.markdown(f"Total **Contract** Net Profit : ${contract_net_profit_total:,.2f}")

with col4:
    st.markdown(f"**Exchange Profit :** ${exchange_net_profit_per_unit:.4f}")
    st.markdown(f"Total **Exchange** Net Profit: ${exchange_net_profit:,.2f}")

st.markdown(f"**Required Exchange Price to Beat Contract (Net):** ${required_exchange_price:.4f}")

# Recommendation Box
if your_exchange_price >= required_exchange_price:
    st.success("✅ Your exchange price is profitable and beats contract-level net returns!")
else:
    st.error("❌ Your exchange price is too low. Contracts would have given better net profit.")

# === Comparison Table ===
with st.expander("🔍 Show Detailed Breakdown Table"):
    df = pd.DataFrame({
        "Metric": [
            "Total Revenue",
            "Transport Cost",
            "Production Cost",
            "Exchange Fee",
            "Net Profit"
        ],
        "Exchange": [
            f"${exchange_revenue:,.2f}",
            f"${exchange_transport_cost:,.2f}",
            f"${exchange_cost:,.2f}",
            f"${exchange_fee:,.2f}",
            f"${exchange_net_profit:,.2f}"
        ],
        "Contract (Benchmark)": [
            f"${contract_revenue:,.2f}",
            f"${contract_transport_cost:,.2f}",
            f"${contract_cost:,.2f}",
            "—",
            f"${contract_net_profit_total:,.2f}"
        ]
    })
    st.table(df)





st.markdown("""
created by **NOXUS TRADER**   

""")

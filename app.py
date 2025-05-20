# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from pathlib import Path

# 1. Page config
st.set_page_config(page_title="🚀 Startup Funding Analyzer", layout="wide")

# 2. Data loading: upload or default
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    @st.cache_data
    def load_data():
        return pd.read_csv("scripts/output/startup_funding.csv", parse_dates=["Date"])
    df = load_data()

# 3. Parse + validate Date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
if df["Date"].isna().all():
    st.error("❌ Could not parse any dates. Make sure your CSV has a valid 'Date' column.")
    st.stop()

# 4. Ensure Amount is numeric + drop invalid rows
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Date", "Amount"])

# 5. Required‑columns check
required_cols = {"Date", "Startup", "Industry", "Location", "Amount", "Type", "YearMonth"}
if not required_cols.issubset(df.columns):
    st.error(f"❌ CSV must contain columns: {required_cols}")
    st.stop()

# 6. App title
st.title("🚀 Startup Funding Analyzer")

# 7. Filters
st.sidebar.header("Filters")
years = df["Date"].dt.year.dropna().astype(int).sort_values().unique()
year_sel = st.sidebar.slider(
    "Year Range",
    int(years.min()), int(years.max()),
    (int(years.min()), int(years.max())),
)
industry_sel = st.sidebar.multiselect(
    "Industry", df["Industry"].unique(), default=df["Industry"].unique()
)
type_sel = st.sidebar.multiselect(
    "Funding Type", df["Type"].unique(), default=df["Type"].unique()
)

# 8. Apply filters
filtered = df[
    df["Date"].dt.year.between(*year_sel) &
    df["Industry"].isin(industry_sel) &
    df["Type"].isin(type_sel)
]

# 9. KPIs
total_funding = filtered["Amount"].sum()
num_startups   = filtered["Startup"].nunique()
num_rounds     = filtered.shape[0]

c1, c2, c3 = st.columns(3)
c1.metric("Total Funding", f"${total_funding/1e6:,.2f}M")
c2.metric("Unique Startups", f"{num_startups}")
c3.metric("Funding Rounds", f"{num_rounds}")

st.markdown("---")

# 10. Funding Over Time
st.header("1. Funding Over Time")
by_ym = (
    filtered.groupby(filtered["Date"].dt.to_period("M"))["Amount"]
    .sum()
    .reset_index()
)
by_ym["Date"] = by_ym["Date"].dt.to_timestamp()
fig1 = px.line(
    by_ym, x="Date", y="Amount",
    title="Monthly Funding Trend",
    labels={"Amount": "Funding (USD)"}
)
fig1.update_yaxes(tickformat=".1s")
st.plotly_chart(fig1, use_container_width=True)

# 11. Forecast next 12 months
st.subheader("1b. Forecast Next 12 Months")
future_df = by_ym.rename(columns={"Date": "ds", "Amount": "y"})
m = Prophet()
with st.spinner("Training forecasting model…"):
    m.fit(future_df)
future = m.make_future_dataframe(periods=12, freq="M")
forecast = m.predict(future)
figf = px.line(
    forecast, x="ds", y="yhat",
    title="Forecasted Monthly Funding",
    labels={"ds": "Date", "yhat": "Forecasted Funding"}
)
st.plotly_chart(figf, use_container_width=True)

st.markdown("---")

# 12. Top Industries
st.header("2. Top Industries by Funding")
top_ind = filtered.groupby("Industry")["Amount"].sum().nlargest(10).reset_index()
fig2 = px.bar(top_ind, x="Amount", y="Industry", orientation="h",
              labels={"Amount": "Funding (USD)"})
st.plotly_chart(fig2, use_container_width=True)

# 13. Top Startups
st.header("3. Top Startups by Funding")
top_start = filtered.groupby("Startup")["Amount"].sum().nlargest(10).reset_index()
fig3 = px.bar(top_start, x="Amount", y="Startup", orientation="h",
              title="Top 10 Startups")
st.plotly_chart(fig3, use_container_width=True)

# 14. Round Counts
st.header("4. Funding Round Counts by Type")
counts = filtered["Type"].value_counts().reset_index()
counts.columns = ["Type", "Count"]
fig4 = px.bar(counts, x="Count", y="Type", orientation="h")
st.plotly_chart(fig4, use_container_width=True)

# 15. Top Locations
st.header("5. Top Locations by Number of Rounds")
top_loc = filtered["Location"].value_counts().nlargest(10).reset_index()
top_loc.columns = ["Location", "Count"]
fig5 = px.bar(top_loc, x="Count", y="Location", orientation="h")
st.plotly_chart(fig5, use_container_width=True)

# 16. Top Investors
st.markdown("---")
st.header("6. Top Investors")
fund_path   = Path("scripts/output/top_investors_by_funding.csv")
rounds_path = Path("scripts/output/top_investors_by_rounds.csv")
if fund_path.exists() and rounds_path.exists():
    inv_fund   = pd.read_csv(fund_path)
    inv_rounds = pd.read_csv(rounds_path)
    ic1, ic2   = st.columns(2)
    with ic1:
        st.subheader("By Total Funding")
        fig6 = px.bar(inv_fund, x="Amount", y="Investor", orientation="h")
        st.plotly_chart(fig6, use_container_width=True)
    with ic2:
        st.subheader("By Number of Rounds")
        fig7 = px.bar(inv_rounds, x="Rounds", y="Investor", orientation="h")
        st.plotly_chart(fig7, use_container_width=True)
else:
    st.warning("⚠️ Run `python scripts/analyze.py` first to generate investor CSVs.")

# 17. Interactive Map of Top Cities
st.markdown("---")
st.header("7. Funding by Top Cities (Map)")
city_counts = filtered["Location"].value_counts().nlargest(10).reset_index()
city_counts.columns = ["City", "Count"]
coords = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai":    (19.0760, 72.8777),
    "Delhi":     (28.7041, 77.1025),
    "Gurgaon":   (28.4595, 77.0266),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai":   (13.0827, 80.2707),
    "Pune":      (18.5204, 73.8567),
    "Kolkata":   (22.5726, 88.3639),
    "Jaipur":    (26.9124, 75.7873),
    "Ahmedabad": (23.0225, 72.5714),
}
city_counts["lat"] = city_counts["City"].map(lambda x: coords.get(x, (None, None))[0])
city_counts["lon"] = city_counts["City"].map(lambda x: coords.get(x, (None, None))[1])
city_counts = city_counts.dropna(subset=["lat", "lon"])
fig_map = px.scatter_mapbox(
    city_counts,
    lat="lat",
    lon="lon",
    size="Count",
    hover_name="City",
    zoom=4,
    height=500,
    size_max=30,
    mapbox_style="open-street-map",
)
st.plotly_chart(fig_map, use_container_width=True)

# 18. Download filtered data
st.markdown("---")
csv = filtered.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_startup_funding.csv",
    mime="text/csv",
)

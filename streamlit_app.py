# streamlit_app.py
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from fetchapi import fetch_opensky_snapshot, fetch_rdu_departures, fetch_aviation_API_airlines_endpoint
import pandas as pd

st.set_page_config(page_title="Flight Volume by Country (OpenSky)", layout="wide")
st.title("🌍 Global Flight Snapshot (via OpenSky Network)")

st.caption("Showing a snapshot of the most recent ~1,800 aircraft globally. Data is live and limited by OpenSky’s API.")

run = st.button("Fetch Live Flights")

# ---------- Main ----------
if run:
    st.info("Fetching live data from OpenSky…")
    try:
        df = fetch_opensky_snapshot()
    except Exception as e:
        st.error(f"Failed to fetch data: {type(e).__name__} -> {e}")
        st.stop()

    st.metric("Flights in snapshot", len(df))

    if df.empty:
        st.warning("No flights found in snapshot.")
        st.stop()

    # Aggregate by country
    summary = df.groupby("origin_country").size().reset_index(name="flights")
    summary = summary.sort_values("flights", ascending=False).head(30)

    # ---------- Plot Top 30 Countries ----------
    st.subheader("✈️ Top 30 Countries by Active Flights")

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(summary["origin_country"], summary["flights"])
    ax.set_xlabel("Flights (current snapshot)")
    ax.set_ylabel("Country")
    ax.set_title("Top 30 Countries by Active Flights")
    ax.invert_yaxis()  # Largest at top
    st.pyplot(fig)

    # ---------- Plot Flight Scatter Map ----------
    st.subheader("🌐 Flight Positions (Scatter Map)")
    df_map = df.dropna(subset=["latitude", "longitude"])

    if df_map.empty:
        st.warning("No geolocation data available for mapping.")
    else:
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.scatter(df_map["longitude"], df_map["latitude"], s=2, alpha=0.5)
        ax2.set_title("Global Flight Positions")
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")
        st.pyplot(fig2)

else:
    st.info("Click 'Fetch Live Flights' to view global snapshot.")

## ---------- RDU Specific Analysis (Arnav) ---------- ##
st.header("🛫 Raleigh-Durham (RDU) Airport Stats")
run_rdu = st.button("Fetch RDU Stats")

if run_rdu:
    with st.spinner("Fetching RDU-specific flight data..."):
        df_departures = fetch_rdu_departures(hours=6)
    
    st.metric("Departures (last 6h)", len(df_departures))

    if not df_departures.empty:
        # ---- Top Airlines ----
        def airline_from_callsign(callsign):
            if not callsign or len(callsign) < 3:
                return "Unknown"
            prefix = callsign[:3].upper()
            mapping = {
                "AAL": "American Airlines",
                "DAL": "Delta",
                "UAL": "United",
                "SWA": "Southwest",
                "JBU": "JetBlue",
                "FDX": "FedEx",
                "UPS": "UPS",
                "NKS": "Spirit",
                "ASA": "Alaska",
                "FFT": "Frontier"
            }
            return mapping.get(prefix, prefix)
        
        df_departures["Airline"] = df_departures["callsign"].apply(airline_from_callsign)
        top_airlines = df_departures["Airline"].value_counts().head(10).reset_index()
        top_airlines.columns = ["Airline", "Flights"]
        st.subheader("🏢 Top 10 Airlines from RDU (last 6h)")
        st.bar_chart(top_airlines.set_index("Airline"))

#### ----------- Airline Profile Comparison (AviationAPI - Ethan Dominic's Code) ----------- ####
airline_data = fetch_aviation_API_airlines_endpoint()

# Local patch: keep running if AviationStack missing/invalid
try:
    _is_missing = not isinstance(airline_data, dict) or "data" not in airline_data
except Exception:
    _is_missing = True
if _is_missing:
    st.warning("AviationStack unavailable; showing empty comparison for local demo.")
    airline_data = {"data": []}

# Graceful fallback when API key is missing/invalid or rate-limited
if not isinstance(airline_data, dict) or "data" not in airline_data:
    st.warning("AviationStack data unavailable (no/invalid AVIATION_KEY or rate limit). Comparison charts will be empty but the page remains usable.")
    

def get_airline_feature_dict(feature_type, cast_type):
    """
    Return a dictionary of airline names along with their values for the specified feature type.
    """
    airline_feature_dict = {}
    for i in range(len(airline_data["data"])):
        airline_name = airline_data["data"][i]["airline_name"]
        if airline_data["data"][i][feature_type] is not None and airline_data["data"][i][feature_type] != "":
            if cast_type == "int":
                airline_feature_value = int(airline_data["data"][i][feature_type])
            elif cast_type == "str":
                airline_feature_value = str(airline_data["data"][i][feature_type])
            else:
                airline_feature_value = float(airline_data["data"][i][feature_type])
        airline_feature_dict[airline_name] = airline_feature_value
    return airline_feature_dict

def plot_bar_graph(feature_series, title, ylabel, bottom_ylim=0):
    """
    Plot a bar graph for the given feature Series.
    """
    fig, ax = plt.subplots()
    bars = ax.bar(feature_series.index.astype(str), feature_series.values)
    ax.set_title(title)
    ax.set_xlabel("Airline")
    ax.set_ylabel(ylabel)
    ax.bar(feature_series.index, feature_series.values)
    ax.bar_label(bars, padding=3)
    plt.xticks(rotation=90)
    plt.ylim(bottom=bottom_ylim)
    st.pyplot(fig)

# Main Program Execution
st.title("Airline Profile Comparison")

comparison_option = st.radio(
    "Pick the type of comparison you would like to see: ",
    ("Fleet Size", "Fleet Average Age", "Founding Year")
)

countries_of_origin = pd.Series(get_airline_feature_dict("country_name", "str"))
country_filters = countries_of_origin.unique().tolist()
country_filters.append("All Countries")
country_filter_option = st.radio(
    "Pick a country of origin to filter by: ",
    (country_filters)
)

if country_filter_option == "All Countries":
    if comparison_option == "Fleet Size":
        fleet_sizes = (pd.Series(get_airline_feature_dict("fleet_size", "int"))).dropna()
        sorted_fleet_sizes = fleet_sizes.sort_values(ascending=True)
        top10_sorted_fleet_sizes = sorted_fleet_sizes.tail(10)
        plot_bar_graph(top10_sorted_fleet_sizes, "Airline Fleet Sizes", "Fleet Size")
    elif comparison_option == "Fleet Average Age":
        fleet_avg_ages = (pd.Series(get_airline_feature_dict("fleet_average_age", "float"))).dropna()
        sorted_fleet_avg_ages = fleet_avg_ages.sort_values(ascending=True)
        top10_sorted_fleet_avg_ages = sorted_fleet_avg_ages.head(10)
        plot_bar_graph(top10_sorted_fleet_avg_ages, "Airline Fleet Average Ages", "Fleet Average Age")
    elif comparison_option == "Founding Year":
        founding_years = (pd.Series(get_airline_feature_dict("date_founded", "int"))).dropna()
        sorted_founding_years = founding_years.sort_values(ascending=True)
        top10_sorted_founding_years = sorted_founding_years.head(10)
        plot_bar_graph(top10_sorted_founding_years, "Airline Founding Years", "Founding Year", bottom_ylim=1900)
else:
    if comparison_option == "Fleet Size":
        fleet_sizes = (pd.Series(get_airline_feature_dict("fleet_size", "int"))).dropna()
        filtered_fleet_sizes = fleet_sizes[countries_of_origin == country_filter_option]
        sorted_fleet_sizes = filtered_fleet_sizes.sort_values(ascending=True)
        plot_bar_graph(sorted_fleet_sizes, "Airline Fleet Sizes", "Fleet Size")
    elif comparison_option == "Fleet Average Age":
        fleet_avg_ages = (pd.Series(get_airline_feature_dict("fleet_average_age", "float"))).dropna()
        filtered_fleet_avg_ages = fleet_avg_ages[countries_of_origin == country_filter_option]
        sorted_fleet_avg_ages = filtered_fleet_avg_ages.sort_values(ascending=True)
        plot_bar_graph(sorted_fleet_avg_ages, "Airline Fleet Average Ages", "Fleet Average Age")
    elif comparison_option == "Founding Year":
        founding_years = (pd.Series(get_airline_feature_dict("date_founded", "int"))).dropna()
        filtered_founding_years = founding_years[countries_of_origin == country_filter_option]
        sorted_founding_years = filtered_founding_years.sort_values(ascending=True)
        plot_bar_graph(sorted_founding_years, "Airline Founding Years", "Founding Year", bottom_ylim=1900)

# ===================== Hanfu's Hourly Heatmap (same page, matching style) =====================
# This block lives at the very bottom so it doesn't touch teammates' code above.

import pandas as pd
import matplotlib.pyplot as plt
from rdu_hourly import hourly_counts_for_day  # local import only for this section

# st.header("🗺️ Airport Hourly Heatmap")

# Controls grouped to match page style
col1, col2, col3 = st.columns([1, 1, 1.2])
with col1:
    # ICAO code input (e.g., KRDU / KJFK / KLAX)
    icao_input = st.text_input("Airport ICAO", value="KRDU")
with col2:
    # IANA timezone used to define the local 'day' for hourly aggregation
    tz_input = st.text_input("Time zone (IANA)", value="America/New_York")
with col3:
    # Default to 'yesterday' because OpenSky arrivals/departures are updated nightly
    _yesterday = (pd.Timestamp.now("America/New_York") - pd.Timedelta(days=1)).date()
    date_input = st.date_input("Local date", value=_yesterday)

# Keep button wording consistent with the page style ("Fetch …")
go_heatmap = st.button("Fetch Heatmap")

# When not triggered, show an info line just like other sections
if not go_heatmap:
    st.info("Click 'Fetch Heatmap' to compute hourly arrivals/departures.")
else:
    # If user selected 'today', auto-switch to 'yesterday' (OpenSky batches previous day)
    _today_local = pd.Timestamp.now(tz_input).date()
    _use_date = date_input
    if date_input == _today_local:
        st.info("OpenSky arrivals/departures are updated nightly. Using yesterday instead of today.")
        _use_date = (_today_local - pd.Timedelta(days=1))

    try:
        # Fetch hourly arrivals/departures for the airport on the local date we determined
        df_hourly = hourly_counts_for_day(icao_input, tz_input, pd.Timestamp(_use_date))
    except Exception as e:
        # Surface any API/auth/timezone errors
        st.error(f"Failed to fetch: {type(e).__name__}: {e}")
        st.stop()

    # If still all zeros, give a helpful hint (small airports / rate limits / batch delay)
    if int(df_hourly["arrivals"].sum()) == 0 and int(df_hourly["departures"].sum()) == 0:
        st.warning("OpenSky returned no flights for that airport/date. Try a larger airport (e.g., KJFK, KLAX) "
                   "or an earlier date (previous days).")

    # Summary metrics
    total_arrivals = int(df_hourly["arrivals"].sum())
    total_departures = int(df_hourly["departures"].sum())
    c1, c2 = st.columns(2)
    c1.metric("Arrivals (day total)", total_arrivals)
    c2.metric("Departures (day total)", total_departures)

    # Show raw hourly table
    st.dataframe(df_hourly, use_container_width=True)

    # Heatmap (2 rows: departures & arrivals; columns: 0..23 local hours)
    matrix = [df_hourly["departures"].tolist(), df_hourly["arrivals"].tolist()]
    fig, ax = plt.subplots(figsize=(10, 2.6))
    im = ax.imshow(matrix, aspect="auto")
    ax.set_yticks([0, 1], labels=["Departures", "Arrivals"])
    ax.set_xticks(range(24))
    ax.set_xlabel("Hour (local)")
# ax.set_title(f"{icao_input.upper()} Hourly Heatmap — {_use_date} ({tz_input})")
    plt.colorbar(im, ax=ax, shrink=0.8)
    st.pyplot(fig)

    # Departures bar chart
    fig2, ax2 = plt.subplots(figsize=(10, 3))
    ax2.bar(df_hourly["hour"], df_hourly["departures"])
    ax2.set_title("Departures by Hour")
    ax2.set_xlabel("Hour (local)")
    ax2.set_ylabel("Flights")
    st.pyplot(fig2)

    # Arrivals bar chart
    fig3, ax3 = plt.subplots(figsize=(10, 3))
    ax3.bar(df_hourly["hour"], df_hourly["arrivals"])
    ax3.set_title("Arrivals by Hour")
    ax3.set_xlabel("Hour (local)")
    ax3.set_ylabel("Flights")
    st.pyplot(fig3)

    # Small note about OpenSky batch behavior (kept low-key to match page tone)
    st.caption("Note: OpenSky arrivals/departures are updated nightly. Yesterday or earlier dates work best.")
# ===================== End Hanfu's Hourly Heatmap =====================
# =====================


# ===================== Demo: Synthetic Multi-Day Table (no API) =====================
# This section generates realistic-looking hourly arrivals/departures for multiple dates
# and shows them in a table on the SAME page. It does NOT call any external API.

import pandas as pd
from demo_mock import gen_demo_hourly_multi_days

st.header("📅 Demo: Multi-Day Hourly Table (Synthetic)")

# Inputs
colA, colB, colC, colD = st.columns([1.1, 1.2, 1, 1])
with colA:
    demo_icao = st.text_input("Airport ICAO (demo)", value="KRDU")
with colB:
    demo_tz = st.text_input("Time zone (IANA, demo)", value="America/New_York")
with colC:
    demo_start = st.date_input("Start date (demo)", value=(pd.Timestamp.now("America/New_York") - pd.Timedelta(days=3)).date())
with colD:
    demo_days = st.slider("Days", min_value=2, max_value=7, value=3, step=1)

if st.button("Generate Demo Data"):
    # Build multi-day synthetic table
    df_demo = gen_demo_hourly_multi_days(demo_icao, demo_tz, pd.Timestamp(demo_start), demo_days)
    st.subheader("Demo Hourly Table")
    st.dataframe(df_demo, use_container_width=True)

    # Per-day totals
    totals = df_demo.groupby("date")[["arrivals","departures"]].sum().reset_index()
    st.subheader("Per-day Totals (Demo)")
    st.dataframe(totals, use_container_width=True)

    # Small note
    st.caption("This is synthetic data for demo only. It does not use any API and is designed for reasonable realism.")
# ===================== End Demo: Synthetic Multi-Day Table =====================

"""Real-Time Healthcare Disease Analysis dashboard.

Reads the Parquet files written by pipeline/run_pipeline.py. If no data is
present yet, it tells the user to run the pipeline first.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import last_updated, load_table

st.set_page_config(page_title="Healthcare Disease Analysis",
                   page_icon="🏥", layout="wide")
st.title("🏥 Real-Time Healthcare Disease Analysis")
st.markdown("Live CDC surveillance data, refreshed automatically by a daily "
            "pipeline. Provisional data — see the freshness stamp on each tab.")

meta = last_updated()
if meta:
    st.caption(f"Last pipeline run: {meta.get('last_run')} | "
               f"Rows loaded: {meta.get('tables', {})}")

nhsn = load_table("nhsn_admissions")
resp = load_table("respnet_rates")
places = load_table("places_chronic")

if nhsn.empty and resp.empty and places.empty:
    st.warning("No processed data found yet. Run `python pipeline/run_pipeline.py` first.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview", "Respiratory Admissions", "Hospitalization Rates", "Chronic Disease"])

with tab1:
    st.header("At a glance")
    if not nhsn.empty:
        latest_week = nhsn["week_ending"].max()
        latest = nhsn[(nhsn["week_ending"] == latest_week) & (nhsn["state"] == "US")]
        st.subheader(f"US new hospital admissions — week ending {latest_week.date()}")
        cols = st.columns(3)
        for col, disease in zip(cols, ["covid", "influenza", "rsv"]):
            row = latest[latest["disease"] == disease]
            value = row["admissions"].sum() if not row.empty else 0
            col.metric(disease.title(), f"{value:,.0f}")
        us = nhsn[nhsn["state"] == "US"].dropna(subset=["admissions"])
        fig = px.line(us, x="week_ending", y="admissions", color="disease",
                      title="US weekly admissions by disease (recent weeks)")
        st.plotly_chart(fig, use_container_width=True)
    if not places.empty:
        st.subheader("Highest chronic-disease prevalence counties (latest release)")
        top = (places.sort_values("prevalence_pct", ascending=False)
               .head(10)[["state", "county", "disease", "prevalence_pct"]])
        st.dataframe(top, use_container_width=True)

with tab2:
    st.header("Weekly respiratory admissions by state (NHSN)")
    if nhsn.empty:
        st.info("NHSN data not loaded yet.")
    else:
        states = sorted(nhsn[nhsn["state"] != "US"]["state"].unique())
        state = st.selectbox("State", states, index=states.index("TX") if "TX" in states else 0)
        diseases = st.multiselect("Disease", ["covid", "influenza", "rsv"],
                                  default=["covid", "influenza", "rsv"])
        data = nhsn[(nhsn["state"] == state) & (nhsn["disease"].isin(diseases))]
        fig = px.line(data, x="week_ending", y="admissions_per_100k",
                      color="disease",
                      title=f"Admissions per 100k — {state}")
        st.plotly_chart(fig, use_container_width=True)
        latest_week = nhsn["week_ending"].max()
        latest = nhsn[(nhsn["week_ending"] == latest_week)
                      & (nhsn["state"] != "US")
                      & (nhsn["disease"].isin(diseases))]
        fig2 = px.bar(latest, x="state", y="admissions_per_100k", color="disease",
                      title=f"Admissions per 100k by state — week ending {latest_week.date()}")
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.header("Hospitalization rates by virus and age group (RESP-NET)")
    if resp.empty:
        st.info("RESP-NET data not loaded yet.")
    else:
        networks = sorted(resp["surveillance_network"].dropna().unique())
        network = st.selectbox("Surveillance network", networks)
        data = resp[resp["surveillance_network"] == network]
        rate_types = sorted(data["rate_type"].dropna().unique())
        rate_type = st.selectbox("Rate type", rate_types)
        data = data[data["rate_type"] == rate_type]
        age_col = "age_category" if "age_category" in data.columns else None
        if age_col:
            ages = sorted(data[age_col].dropna().unique())
            age = st.selectbox("Age group", ages)
            data = data[data[age_col] == age]
        fig = px.line(data, x="date", y="estimate",
                      title=f"Hospitalization rate — {network}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(data.sort_values("date", ascending=False).head(20),
                     use_container_width=True)

with tab4:
    st.header("Chronic disease prevalence by county (PLACES)")
    if places.empty:
        st.info("PLACES data not loaded yet.")
    else:
        disease = st.selectbox("Condition", sorted(places["disease"].unique()))
        data = places[places["disease"] == disease]
        st.metric("Counties covered", f"{len(data):,}")
        top = data.sort_values("prevalence_pct", ascending=False).head(15)
        fig = px.bar(top, x="prevalence_pct", y="county", color="state",
                     orientation="h",
                     title=f"Top 15 counties — {disease} prevalence (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(data.sort_values("prevalence_pct", ascending=False).head(50),
                     use_container_width=True)

st.caption("Sources: CDC NHSN (vdzy-6i9v), CDC RESP-NET (kvib-3txy), "
           "CDC PLACES (cwsq-ngmh). Analytics portfolio project — not medical advice.")

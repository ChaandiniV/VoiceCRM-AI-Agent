from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_PATH = Path(os.getenv("DATABASE_PATH", "data/voicecrm.db"))

st.set_page_config(page_title="VoiceCRM AI Agent Dashboard", layout="wide")
st.title("VoiceCRM AI Agent — Implementation Dashboard")
st.caption("Monitor AI voice calls, qualified leads, CRM sync status, and webhook events.")


def read_table(table: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table} ORDER BY id DESC", conn)


calls = read_table("calls")
leads = read_table("leads")
transcripts = read_table("transcripts")
webhooks = read_table("webhook_events")

if calls.empty and leads.empty:
    st.warning("No data yet. Start the FastAPI backend and run `python scripts/demo_call.py` to generate a sample call.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Calls", len(calls))
col2.metric("Qualified Leads", len(leads))
if not leads.empty:
    col3.metric("Avg Lead Score", round(leads["lead_score"].mean(), 1))
    col4.metric("High Priority Leads", int((leads["priority"] == "High").sum()))
else:
    col3.metric("Avg Lead Score", 0)
    col4.metric("High Priority Leads", 0)

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Lead Pipeline")
    if not leads.empty:
        st.dataframe(
            leads[[
                "id",
                "customer_name",
                "company",
                "industry",
                "lead_score",
                "priority",
                "next_action",
                "crm_status",
                "created_at",
            ]],
            use_container_width=True,
        )
    else:
        st.info("No leads available yet.")

with right:
    st.subheader("Priority Breakdown")
    if not leads.empty:
        st.bar_chart(leads["priority"].value_counts())
    else:
        st.info("Run a demo call to see priority distribution.")

st.subheader("Call Logs")
if not calls.empty:
    st.dataframe(calls, use_container_width=True)
else:
    st.info("No calls logged yet.")

st.subheader("Transcripts")
if not transcripts.empty:
    selected_call = st.selectbox("Select call ID", sorted(transcripts["call_id"].unique(), reverse=True))
    selected = transcripts[transcripts["call_id"] == selected_call].sort_values("id")
    for _, row in selected.iterrows():
        st.markdown(f"**{row['speaker'].title()}:** {row['message']}")
else:
    st.info("No transcripts logged yet.")

st.subheader("Webhook Events")
if not webhooks.empty:
    st.dataframe(webhooks, use_container_width=True)
else:
    st.info("No webhook events logged yet.")

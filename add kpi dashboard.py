import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------- 1. PAGE SETUP ----------------

st.set_page_config(
    page_title="OPD Hospital & Doctor Analytics Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ---------------- PASSWORD PROTECTION ----------------

def check_password():
    if st.session_state.get("authenticated", False):
        return True

    st.title("🔐 Secure Dashboard Login")
    st.write("Please enter the password to access the dashboard.")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):
        if password == st.secrets["DASHBOARD_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")

    return False


if not check_password():
    st.stop()


# ---------------- 2. DATA LOADING ----------------

@st.cache_data
def load_data(file_path):
    excel_file = pd.ExcelFile(file_path)

    df_raw = pd.read_excel(excel_file, sheet_name="Sheet1")
    df_top = pd.read_excel(excel_file, sheet_name="Top 10")
    df_kpi = pd.read_excel(excel_file, sheet_name="KPI Summary")

    return df_raw, df_top, df_kpi

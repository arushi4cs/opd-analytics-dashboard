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

st.title("🏥 OPD Performance & Claims Analytics Dashboard")
st.caption("Detailed overview of Hospitals, Doctors, High-Value Transactions, and Treatment Distribution")

# ---------------- 2. DATA LOADING ----------------
@st.cache_data
def load_data(file_path):
    excel_file = pd.ExcelFile(file_path)
    
    # Raw Data
    df_raw = pd.read_excel(excel_file, sheet_name="Sheet1")
    
    # Top 10 Data
    df_top = pd.read_excel(excel_file, sheet_name="Top 10")
    
    # KPI Data
    df_kpi = pd.read_excel(excel_file, sheet_name="KPI Summary")
    
    return df_raw, df_top, df_kpi

# अपनी फ़ाइल का सही पाथ यहाँ दें या उसी फ़ोल्डर में रखें
FILE_PATH = "Top10_Hospital_Doctor.xlsx"

try:
    df_raw, df_top, df_kpi = load_data(FILE_PATH)
    
    # ---------------- 3. SIDEBAR FILTERS ----------------
    st.sidebar.header("🔍 Filters & Controls")
    
    districts = ["All Districts"] + sorted(df_raw["DISTRICTNAME"].dropna().unique().tolist())
    selected_district = st.sidebar.selectbox("Select District:", districts)
    
    # फ़िल्टर लागू करें
    if selected_district != "All Districts":
        filtered_df = df_raw[df_raw["DISTRICTNAME"] == selected_district]
    else:
        filtered_df = df_raw.copy()
        
    # ---------------- 4. TOP KPI CARDS ----------------
    st.subheader("📌 Key Performance Indicators (KPIs)")
    
    total_claims = filtered_df["TOTAL_CLAIMS"].sum()
    total_hospitals = filtered_df["HOSPITALNAME"].nunique()
    total_doctors = filtered_df["TREATINGDOCTORNAME"].nunique()
    total_allopathic = filtered_df["ALLOPATHIC_COUNT"].sum()
    total_ayurvedic = filtered_df["AYURVEDIC_COUNT"].sum()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Claims", f"{total_claims:,}")
    k2.metric("Active Hospitals", f"{total_hospitals:,}")
    k3.metric("Active Doctors", f"{total_doctors:,}")
    k4.metric("Allopathic / Ayurvedic", f"{total_allopathic:,} / {total_ayurvedic:,}")
    
    st.divider()

    # ---------------- 5. CHARTS: TOP 10 HOSPITALS & DOCTORS ----------------
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏥 Top 10 Hospitals by Claims")
        top_hosp = (
            filtered_df.groupby("HOSPITALNAME")["TOTAL_CLAIMS"]
            .sum()
            .reset_index()
            .sort_values(by="TOTAL_CLAIMS", ascending=False)
            .head(10)
        )
        fig_hosp = px.bar(
            top_hosp,
            x="TOTAL_CLAIMS",
            y="HOSPITALNAME",
            orientation="h",
            text="TOTAL_CLAIMS",
            color="TOTAL_CLAIMS",
            color_continuous_scale="Blues"
        )
        fig_hosp.update_layout(yaxis=dict(autorange="reversed"), yaxis_title="", xaxis_title="Total Claims")
        st.plotly_chart(fig_hosp, width='stretch')

    with c2:
        st.subheader("👨‍⚕️ Top 10 Doctors by Claims")
        top_doc = (
            filtered_df.groupby("TREATINGDOCTORNAME")["TOTAL_CLAIMS"]
            .sum()
            .reset_index()
            .sort_values(by="TOTAL_CLAIMS", ascending=False)
            .head(10)
        )
        fig_doc = px.bar(
            top_doc,
            x="TOTAL_CLAIMS",
            y="TREATINGDOCTORNAME",
            orientation="h",
            text="TOTAL_CLAIMS",
            color="TOTAL_CLAIMS",
            color_continuous_scale="Teal"
        )
        fig_doc.update_layout(yaxis=dict(autorange="reversed"), yaxis_title="", xaxis_title="Total Claims")
        st.plotly_chart(fig_doc, width='stretch')

    st.divider()

    # ---------------- 6. DISTRICT DISTRIBUTION & HIGH VALUE TIDs ----------------
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("🏙️ Top Districts by Claim Volume")
        dist_summary = (
            df_raw.groupby("DISTRICTNAME")["TOTAL_CLAIMS"]
            .sum()
            .reset_index()
            .sort_values(by="TOTAL_CLAIMS", ascending=False)
            .head(8)
        )
        fig_dist = px.pie(
            dist_summary,
            names="DISTRICTNAME",
            values="TOTAL_CLAIMS",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_dist, width='stretch')

    with c4:
        st.subheader("💳 Top 10 High-Value Transactions (TID)")
        # Top 10 Sheet से ट्रांजेक्शन डेटा
        tid_data = df_top[["TRANSACTIONID", "AMOUNTTOCLAIM", "TYPE"]].dropna().head(10)
        tid_data["TRANSACTIONID"] = tid_data["TRANSACTIONID"].astype(str)
        tid_data["AMOUNTTOCLAIM"] = tid_data["AMOUNTTOCLAIM"].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(tid_data, width='stretch', hide_index=True)

    st.divider()

    # ---------------- 7. DETAILED DATA VIEW & DOWNLOAD ----------------
    st.subheader("📋 Detailed Claims Data")
    st.dataframe(filtered_df, width='stretch')

    # Excel Download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Filtered_Data")
        
    st.download_button(
        label="📥 Download Filtered Data (Excel)",
        data=buffer.getvalue(),
        file_name="Filtered_OPD_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

except Exception as e:
    st.error(f"फ़ाइल लोड करने में समस्या: {e}")
    st.info("सुनिश्चित करें कि 'Top10_Hospital_Doctor.xlsx' फ़ाइल उसी फ़ोल्डर में मौजूद है जहाँ यह स्क्रिप्ट है।")
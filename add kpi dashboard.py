import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="Professional Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Subtle & Clean)
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# ----------------- HEADER SECTION -----------------
st.title("📊 Executive Business Dashboard")
st.caption("Interactive Insights & Analytics from Excel Data")

# ----------------- SIDEBAR: DATA SOURCE -----------------
st.sidebar.header("⚙️ Data Settings")

uploaded_file = st.sidebar.file_uploader(
    "Upload your Excel File (.xlsx / .xls)", 
    type=["xlsx", "xls"]
)

# Function to load sample data if user hasn't uploaded yet
@st.cache_data
def load_sample_data():
    sample_data = {
        'Date': pd.date_range(start='2026-01-01', periods=100, freq='D'),
        'Region': ['North', 'South', 'East', 'West'] * 25,
        'Category': ['Electronics', 'Furniture', 'Clothing', 'Office Supplies'] * 25,
        'Sales': [1500, 3200, 450, 1200, 2800, 950, 4100, 600] * 12 + [1500, 3200, 450, 1200],
        'Profit': [300, 800, 90, 240, 560, 190, 820, 120] * 12 + [300, 800, 90, 240],
        'Quantity': [5, 12, 3, 8, 10, 4, 15, 2] * 12 + [5, 12, 3, 8]
    }
    return pd.DataFrame(sample_data)

if uploaded_file is not None:
    try:
        # Load user Excel file
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Excel sheet loaded successfully!")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        st.stop()
else:
    df = load_sample_data()
    st.info("ℹ️ Abhi sample data display ho raha hai. Apna custom data dekhne ke liye sidebar se Excel file upload karein.")

# ----------------- SIDEBAR: FILTERS -----------------
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

# Identifying categorical columns dynamically
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

filtered_df = df.copy()

if categorical_cols:
    for col in categorical_cols[:3]: # First 3 categorical filters
        unique_vals = list(df[col].dropna().unique())
        selected_vals = st.sidebar.multiselect(
            f"Select {col}:",
            options=unique_vals,
            default=unique_vals
        )
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

# ----------------- KPI / METRIC CARDS -----------------
st.markdown("### 📈 Key Performance Indicators (KPIs)")

numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()

if numeric_cols:
    kpi_cols = st.columns(min(len(numeric_cols), 4))
    for i, col_name in enumerate(numeric_cols[:4]):
        total_val = filtered_df[col_name].sum()
        avg_val = filtered_df[col_name].mean()
        with kpi_cols[i]:
            st.metric(
                label=f"Total {col_name}",
                value=f"{total_val:,.2f}" if isinstance(total_val, float) else f"{total_val:,}",
                delta=f"Avg: {avg_val:,.1f}"
            )

st.markdown("---")

# ----------------- VISUALIZATIONS & CHARTS -----------------
col_chart1, col_chart2 = st.columns(2)

# Chart 1: Bar Chart / Breakdown
with col_chart1:
    st.subheader("📌 Category / Segment Distribution")
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        
        fig1 = px.bar(
            filtered_df.groupby(cat_col, as_index=False)[num_col].sum(),
            x=cat_col,
            y=num_col,
            text_auto='.2s',
            title=f"{num_col} by {cat_col}",
            color=cat_col,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig1.update_layout(showlegend=False, template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("Visualizations ke liye numeric aur categorical columns required hain.")

# Chart 2: Correlation / Scatter or Donut
with col_chart2:
    st.subheader("🥧 Proportional Share")
    if len(categorical_cols) >= 2 and numeric_cols:
        cat_col_2 = categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0]
        num_col = numeric_cols[0]
        
        fig2 = px.pie(
            filtered_df,
            names=cat_col_2,
            values=num_col,
            title=f"{num_col} Breakdown by {cat_col_2}",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_layout(template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)
    elif len(numeric_cols) >= 2:
        fig2 = px.scatter(
            filtered_df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
            template="plotly_white"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ----------------- DETAILED DATA TABLE -----------------
st.markdown("---")
with st.expander("📋 View & Download Filtered Data Table", expanded=False):
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download filtered CSV button
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_dashboard_data.csv",
        mime="text/csv"
    )


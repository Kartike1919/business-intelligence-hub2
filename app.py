import io
import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(
    page_title="Business Intelligence Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
    /* App background */
    .stApp { background-color: #0f172a; }
    .block-container { padding-top: 0.5rem !important; }

    /* Hide default streamlit header */
    header[data-testid="stHeader"] {
        background-color: #0f172a !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        border-right: 1px solid #334155 !important;
    }

    /* Upload box */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #1e293b, #1e1b4b) !important;
        border: 2px dashed #6366f1 !important;
        border-radius: 16px !important;
        padding: 8px !important;
        box-shadow: 0 0 20px rgba(99,102,241,0.15) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] div span {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] div small {
        color: #64748b !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.4) !important;
    }
    [data-testid="stFileUploaderFile"] {
        background: rgba(99,102,241,0.1) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b, #1e1b4b);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.75rem !important; }
    [data-testid="stMetricValue"] { color: #e2e8f0 !important; font-weight: 800 !important; }

    /* Sidebar text */
    [data-testid="stSidebar"] .stMarkdown p { color: #94a3b8 !important; }
    [data-testid="stSidebar"] label { color: #a5b4fc !important; font-weight: 600 !important; }
</style>
""",
    unsafe_allow_html=True,
)


COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4']
DARK_TEMPLATE = dict(
    template='plotly_dark',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,23,42,0.8)',
)


@st.cache_data
def load_data(file) -> pd.DataFrame:
    return pd.read_csv(file)


def sample_csv_bytes() -> bytes:
    sample = pd.DataFrame(
        {
            "Order Date": pd.date_range(datetime.today(), periods=8, freq="D"),
            "Category": ["Electronics", "Fashion", "Home", "Home", "Fashion", "Beauty", "Electronics", "Home"],
            "Amount": [1200, 340, 890, 560, 420, 310, 990, 710],
        }
    )
    return sample.to_csv(index=False).encode("utf-8")


def metric_delta(value: float, median: float) -> str:
    if median == 0 or pd.isna(median) or pd.isna(value):
        return "0"
    delta = (value / median - 1) * 100
    return f"{delta:+.1f}%"


def chart_card_start(title: str) -> None:
    st.markdown(
        f"""
<div style="background:#1e293b; border-radius:16px; 
    padding:20px; border:1px solid #334155; 
    box-shadow:0 4px 20px rgba(0,0,0,0.3); margin-bottom:16px;">
<h4 style="color:white; margin:0 0 10px 0;">{title}</h4>
""",
        unsafe_allow_html=True,
    )


def chart_card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


# --- Top nav bar ---
st.markdown(
    """
<div style="background:linear-gradient(90deg,#0f172a,#1e1b4b,#0f172a);border-bottom:1px solid #334155;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;border-radius:0 0 12px 12px;">
    <div style="display:flex;gap:28px;align-items:center;">
        <span style="color:#6366f1;font-size:0.8rem;font-weight:700;border-bottom:2px solid #6366f1;padding-bottom:2px;">📊 Dashboard</span>
        <span style="color:#64748b;font-size:0.8rem;">📁 Data</span>
        <span style="color:#64748b;font-size:0.8rem;">💡 Insights</span>
        <span style="color:#64748b;font-size:0.8rem;">📤 Export</span>
    </div>
    <div style="display:flex;gap:12px;align-items:center;">
        <span style="background:rgba(99,102,241,0.15);color:#a5b4fc;border:1px solid #6366f1;padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;">⚡ Powered by AI</span>
        <span style="background:rgba(16,185,129,0.12);color:#6ee7b7;border:1px solid #10b981;padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;">🔒 Private & Secure</span>
        <span style="background:rgba(245,158,11,0.12);color:#fcd34d;border:1px solid #f59e0b;padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;">v1.0 BETA</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        """
<div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
    border-radius:10px;padding:10px;text-align:center;margin:8px 0;">
    <span style="color:white;font-weight:800;font-size:0.9rem;">📊 DataLens Analytics</span>
</div>
""",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])


if uploaded_file is None:
    st.markdown(
        """
<div style="
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 100%);
    border-radius: 20px;
    padding: 40px;
    margin-bottom: 30px;
    border: 1px solid #6366f1;
    box-shadow: 0 0 40px rgba(99,102,241,0.3);
">
    <h1 style="color:white; font-size:2.5rem; margin:0; font-weight:800; letter-spacing:-1px;">
        📊 Business Intelligence Hub
    </h1>
    <p style="color:#a5b4fc; font-size:1.1rem; margin-top:10px;">
        Turn your data into decisions — instantly.
    </p>
    <div style="display:flex; gap:20px; margin-top:20px; flex-wrap:wrap;">
        <span style="background:rgba(99,102,241,0.3); color:#c7d2fe; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #6366f1;">
            ⚡ Real-time Analysis
        </span>
        <span style="background:rgba(16,185,129,0.2); color:#6ee7b7; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #10b981;">
            📈 Auto KPIs
        </span>
        <span style="background:rgba(245,158,11,0.2); color:#fcd34d; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #f59e0b;">
            🎯 Smart Insights
        </span>
        <span style="background:rgba(236,72,153,0.2); color:#f9a8d4; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #ec4899;">
            🗂️ CSV Upload
        </span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div style="text-align:center; margin-top:24px;">
    <div style="width:72px;height:72px;border-radius:50%;background:rgba(99,102,241,0.2);
        display:inline-flex;align-items:center;justify-content:center;box-shadow:0 0 25px rgba(99,102,241,0.5);">
        <span style="font-size:1.8rem;">📤</span>
    </div>
    <h2 style="color:white; margin-top:16px;">Welcome to Business Intelligence Hub</h2>
    <p style="color:#94a3b8;">Upload a CSV and unlock instant performance insights.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    feature_cols = st.columns(3)
    feature_cols[0].markdown("**Performance KPIs**")
    feature_cols[0].caption("Revenue, growth, and category insights in seconds.")
    feature_cols[1].markdown("**Smart Visuals**")
    feature_cols[1].caption("Auto-generated charts built for decision-making.")
    feature_cols[2].markdown("**Data Quality**")
    feature_cols[2].caption("Quick checks for missing values and duplicates.")
    st.download_button(
        "Download sample CSV",
        data=sample_csv_bytes(),
        file_name="sample_datalens.csv",
        mime="text/csv",
    )
    st.stop()


with st.spinner("⏳ Analyzing your data..."):
    try:
        df = load_data(uploaded_file)
    except Exception:
        st.error("Unable to read this file. Please upload a valid CSV.")
        st.stop()

st.session_state["df"] = df

progress = st.progress(0, text="🔄 Building dashboard...")
for i in range(100):
    time.sleep(0.008)
    progress.progress(i + 1, text=f"🔄 Processing... {i+1}%")
progress.empty()
st.toast("✅ Dashboard ready!", icon="🎉")


if df.empty:
    st.error("The uploaded CSV is empty.")
    st.stop()

date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
num_cols = df.select_dtypes(include=["number"]).columns.tolist()

with st.sidebar:
    st.markdown("### Dataset Info")
    st.markdown(f"**Rows:** {len(df):,}")
    st.markdown(f"**Columns:** {len(df.columns)}")
    st.markdown(f"**File size:** {uploaded_file.size/1024:.1f} KB")

    st.markdown("### Column Selectors")
    date_col = st.selectbox(
        "Date Column",
        options=date_cols or ["None"],
        index=0,
        label_visibility="collapsed",
    )
    cat_col = st.selectbox(
        "Category Column",
        options=cat_cols or ["None"],
        index=0,
        label_visibility="collapsed",
    )
    num_col = st.selectbox(
        "Numeric Column",
        options=num_cols or ["None"],
        index=0,
        label_visibility="collapsed",
    )


missing_pct = round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 1)
numeric_count = len(num_cols)
st.markdown(
    f"""
<div style="
    background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 1px solid #1e293b;
    padding: 10px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    border-radius: 12px;
">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:1.4rem;">📊</span>
        <span style="color:#e2e8f0; font-weight:700; font-size:1rem; letter-spacing:0.5px;">
            Business Intelligence Hub
        </span>
        <span style="
            background:#6366f1; color:white;
            font-size:0.65rem; padding:2px 8px;
            border-radius:10px; font-weight:600;
        ">BETA</span>
    </div>
    <div style="display:flex; gap:24px; align-items:center;">
        <div style="text-align:center;">
            <div style="color:#6366f1; font-size:1rem; font-weight:700;">{len(df):,}</div>
            <div style="color:#64748b; font-size:0.65rem;">ROWS</div>
        </div>
        <div style="text-align:center;">
            <div style="color:#8b5cf6; font-size:1rem; font-weight:700;">{len(df.columns)}</div>
            <div style="color:#64748b; font-size:0.65rem;">COLUMNS</div>
        </div>
        <div style="text-align:center;">
            <div style="color:#10b981; font-size:1rem; font-weight:700;">{numeric_count}</div>
            <div style="color:#64748b; font-size:0.65rem;">METRICS</div>
        </div>
        <div style="text-align:center;">
            <div style="color:#f59e0b; font-size:1rem; font-weight:700;">{missing_pct}%</div>
            <div style="color:#64748b; font-size:0.65rem;">MISSING</div>
        </div>
        <span style="
            background: rgba(16,185,129,0.15);
            color:#10b981;
            border:1px solid #10b981;
            padding:4px 14px;
            border-radius:20px;
            font-size:0.75rem;
            font-weight:600;
        ">● LIVE</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


filename = uploaded_file.name
st.markdown(
    f"""
<div style="
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 100%);
    border-radius: 20px;
    padding: 40px;
    margin-bottom: 30px;
    border: 1px solid #6366f1;
    box-shadow: 0 0 40px rgba(99,102,241,0.3);
">
    <h1 style="color:white; font-size:2.5rem; margin:0; font-weight:800; letter-spacing:-1px;">
        📊 Business Intelligence Hub
    </h1>
    <p style="color:#a5b4fc; font-size:1.1rem; margin-top:10px;">
        Turn your data into decisions — instantly.
    </p>
    <div style="display:flex; gap:20px; margin-top:20px; flex-wrap:wrap;">
        <span style="background:rgba(99,102,241,0.3); color:#c7d2fe; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #6366f1;">
            ⚡ Real-time Analysis
        </span>
        <span style="background:rgba(16,185,129,0.2); color:#6ee7b7; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #10b981;">
            📈 Auto KPIs
        </span>
        <span style="background:rgba(245,158,11,0.2); color:#fcd34d; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #f59e0b;">
            🎯 Smart Insights
        </span>
        <span style="background:rgba(236,72,153,0.2); color:#f9a8d4; padding:6px 16px; border-radius:20px; font-size:0.85rem; border:1px solid #ec4899;">
            🗂️ CSV Upload
        </span>
    </div>
    <div style="margin-top:18px; color:#c7d2fe; font-size:0.9rem;">
        📁 {filename} • 📋 {len(df):,} rows • 🔢 {len(df.columns)} columns • ✅ Ready
    </div>
</div>
""",
    unsafe_allow_html=True,
)


st.markdown("## Performance KPIs")
if num_cols:
    metrics = [("TOTAL RECORDS", float(len(df)), float(len(df)))]
    for col in num_cols[:6]:
        series = df[col].dropna()
        median = series.median()
        metrics.extend(
            [
                (f"{col.upper()} SUM", series.sum(), median),
                (f"{col.upper()} MEAN", series.mean(), median),
                (f"{col.upper()} MAX", series.max(), median),
                (f"{col.upper()} MIN", series.min(), median),
            ]
        )

    rows = (len(metrics) + 3) // 4
    idx = 0
    for _ in range(rows):
        cols = st.columns(4)
        for col in cols:
            if idx >= len(metrics):
                break
            label, value, median = metrics[idx]
            value_fmt = f"{value:,.2f}" if label != "TOTAL RECORDS" else f"{int(value):,}"
            col.metric(label, value_fmt, metric_delta(value, median))
            idx += 1
else:
    st.info("No numeric columns found for KPI calculations.")


st.markdown("## 📊 Smart Charts")
st.markdown("*Auto-generated from your data*")

best_num_col = None
if num_cols:
    sums = df[num_cols].sum(numeric_only=True)
    if not sums.empty:
        best_num_col = sums.idxmax()

best_cat_col = None
if cat_cols:
    candidates = [c for c in cat_cols if 5 <= df[c].nunique(dropna=True) <= 50]
    if candidates:
        best_cat_col = max(candidates, key=lambda c: df[c].nunique(dropna=True))

chart_card_start("📅 Sales Trend Over Time")
if best_num_col and date_cols:
    date_series = pd.to_datetime(df[date_cols[0]], errors='coerce')
    monthly = df.assign(_date=date_series).dropna(subset=["_date"])
    monthly = monthly.groupby(monthly["_date"].dt.to_period('M'))[best_num_col].sum().reset_index()
    monthly["_date"] = monthly["_date"].astype(str)
    fig = px.area(monthly, x="_date", y=best_num_col, color_discrete_sequence=['#6366f1'])
    fig.update_traces(fill='tozeroy', fillcolor='rgba(99,102,241,0.15)', line_color='#6366f1', line_width=2.5)
    fig.update_layout(**DARK_TEMPLATE, height=320, title_font_color='white', xaxis_title='', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 Add a date column to see trends over time.")
chart_card_end()

col_left, col_right = st.columns([1, 1])
with col_left:
    chart_card_start("🏆 Top 10 Performers")
    if best_cat_col and best_num_col:
        top10 = df.groupby(best_cat_col)[best_num_col].sum().nlargest(10).reset_index()
        fig = px.bar(
            top10,
            x=best_num_col,
            y=best_cat_col,
            orientation='h',
            color=best_num_col,
            color_continuous_scale=['#312e81', '#6366f1', '#a5b4fc'],
        )
        fig.update_layout(**DARK_TEMPLATE, height=380, yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
        fig.update_traces(texttemplate='%{x:,.0f}', textposition='outside', textfont_color='#94a3b8')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Add a categorical and numeric column to see top performers.")
    chart_card_end()

with col_right:
    chart_card_start("🥧 Category Breakdown")
    if best_cat_col and best_num_col:
        cat_sum = df.groupby(best_cat_col)[best_num_col].sum().sort_values(ascending=False)
        top7 = cat_sum.head(7)
        others = cat_sum.iloc[7:].sum() if len(cat_sum) > 7 else 0
        pie_df = top7.reset_index()
        pie_df.columns = [best_cat_col, best_num_col]
        if others > 0:
            pie_df = pd.concat(
                [pie_df, pd.DataFrame({best_cat_col: ["Others"], best_num_col: [others]})],
                ignore_index=True,
            )
        fig = px.pie(
            pie_df,
            values=best_num_col,
            names=best_cat_col,
            hole=0.55,
            color_discrete_sequence=COLORS,
        )
        fig.update_traces(textposition='outside', textinfo='percent+label', pull=[0.05] + [0] * (len(pie_df) - 1))
        fig.update_layout(**DARK_TEMPLATE, height=380, showlegend=False)
        fig.add_annotation(
            text=f"Total<br><b>{df[best_num_col].sum():,.0f}</b>",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color='white', size=14),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Add a categorical and numeric column to see breakdowns.")
    chart_card_end()

chart_card_start("📊 Performance Scorecard")
second_cat = None
if cat_cols:
    candidates = [c for c in cat_cols if c != best_cat_col and 5 <= df[c].nunique(dropna=True) <= 50]
    if candidates:
        second_cat = max(candidates, key=lambda c: df[c].nunique(dropna=True))
if second_cat and best_num_col:
    top8 = df[second_cat].value_counts().head(8).index
    grouped = df[df[second_cat].isin(top8)].groupby(second_cat)
    sums = grouped[best_num_col].sum()
    means = grouped[best_num_col].mean()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=sums.index, y=sums.values, name='Total', marker_color='#6366f1', opacity=0.85),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=means.index,
            y=means.values,
            name='Average',
            mode='lines+markers',
            line=dict(color='#f59e0b', width=2.5),
            marker=dict(size=8, color='#f59e0b'),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        **DARK_TEMPLATE,
        height=340,
        barmode='group',
        title=f"📊 {best_num_col} — Total vs Average per Category",
        title_font_color='white',
        legend=dict(bgcolor='rgba(0,0,0,0)', font_color='#94a3b8'),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 Add another categorical column to see a scorecard.")
chart_card_end()

rows_html = ""
if num_cols:
    for col in num_cols:
        total = df[col].sum()
        mean = df[col].mean()
        mx = df[col].max()
        pct = min(100, int((mean / mx) * 100)) if mx != 0 else 0
        rows_html += f"""
    <tr>
        <td style="color:#e2e8f0; font-weight:600; padding:10px 16px;">{col}</td>
        <td style="color:#a5b4fc; padding:10px;">{total:,.1f}</td>
        <td style="color:#6ee7b7; padding:10px;">{mean:,.2f}</td>
        <td style="color:#fcd34d; padding:10px;">{mx:,.1f}</td>
        <td style="padding:10px; min-width:120px;">
            <div style="background:#1e293b; border-radius:6px; height:8px; width:100%;">
                <div style="background:linear-gradient(90deg,#6366f1,#8b5cf6); 
                    width:{pct}%; height:8px; border-radius:6px;"></div>
            </div>
        </td>
    </tr>"""
    st.markdown(
        f"""
<div style="background:#1e293b; border-radius:16px; padding:20px; 
    border:1px solid #334155; margin-top:16px;">
    <h4 style="color:white; margin-bottom:16px;">🔥 Key Metrics Summary</h4>
    <table style="width:100%; border-collapse:collapse;">
        <thead>
            <tr style="border-bottom:1px solid #334155;">
                <th style="color:#64748b; text-align:left; padding:8px 16px; font-size:0.75rem;">COLUMN</th>
                <th style="color:#64748b; text-align:left; padding:8px; font-size:0.75rem;">TOTAL</th>
                <th style="color:#64748b; text-align:left; padding:8px; font-size:0.75rem;">AVERAGE</th>
                <th style="color:#64748b; text-align:left; padding:8px; font-size:0.75rem;">MAX</th>
                <th style="color:#64748b; text-align:left; padding:8px; font-size:0.75rem;">DISTRIBUTION</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown("## 🚀 Deep Dive Analysis")
st.markdown("*Three powerful views to understand your business deeper*")

if best_cat_col and best_num_col:
    chart_card_start("🏆 Top 10 Performers")
    top10 = df.groupby(best_cat_col)[best_num_col].sum().nlargest(10).reset_index()
    fig = px.bar(top10, x=best_num_col, y=best_cat_col, orientation='h', color_discrete_sequence=['#6366f1'])
    fig.update_layout(**DARK_TEMPLATE, height=320, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    chart_card_end()

    col_a, col_b = st.columns([1, 1])
    with col_a:
        chart_card_start("📦 Distribution by Category")
        fig = px.box(df, x=best_cat_col, y=best_num_col, color_discrete_sequence=COLORS)
        fig.update_layout(**DARK_TEMPLATE, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Wide boxes = high variation. Dots = outliers.")
        chart_card_end()
    with col_b:
        chart_card_start("📅 Monthly Comparison")
        if date_cols:
            date_series = pd.to_datetime(df[date_cols[0]], errors='coerce')
            monthly = df.assign(_date=date_series).dropna(subset=["_date"])
            monthly = monthly.groupby([monthly["_date"].dt.to_period('M'), best_cat_col])[best_num_col].sum().reset_index()
            monthly["_date"] = monthly["_date"].astype(str)
            top_cats = df.groupby(best_cat_col)[best_num_col].sum().nlargest(5).index
            monthly = monthly[monthly[best_cat_col].isin(top_cats)]
            fig = px.bar(monthly, x="_date", y=best_num_col, color=best_cat_col, barmode="group")
            fig.update_layout(**DARK_TEMPLATE, height=360)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Add a date column for monthly comparisons.")
        chart_card_end()


st.markdown("## 💡 Smart Insights")
st.markdown("*Auto-detected patterns in your data*")

insights = []
if best_cat_col and best_num_col:
    grouped = df.groupby(best_cat_col)[best_num_col].sum()
    top_cat = grouped.idxmax()
    top_val = grouped.max()
    insights.append(("success", f"🏆 **Top performer:** {top_cat} leads with {top_val:,.0f} in {best_num_col}"))
    bottom_cat = grouped.idxmin()
    insights.append(("error", f"📉 **Needs attention:** {bottom_cat} is the lowest performing segment"))

missing = df.isnull().sum()
if missing.any():
    worst_col = missing.idxmax()
    insights.append(("warning", f"⚠️ **Missing data:** Column '{worst_col}' has {missing.max()} missing values"))

if date_cols and best_num_col:
    date_series = pd.to_datetime(df[date_cols[0]], errors='coerce')
    monthly = df.assign(_date=date_series).dropna(subset=["_date"])
    monthly = monthly.groupby(monthly["_date"].dt.to_period('M'))[best_num_col].sum()
    if not monthly.empty:
        peak = monthly.idxmax()
        insights.append(("info", f"📈 **Peak period:** {peak} was your best performing month"))

insights.append(("info", f"📊 **Dataset size:** {len(df):,} records across {len(df.columns)} columns analyzed"))

for kind, message in insights:
    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    elif kind == "error":
        st.error(message)
    else:
        st.info(message)


with st.expander("🗂️ View Raw Data & Quality Report"):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", f"{len(df):,}")
    col2.metric("Total Columns", len(df.columns))
    col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")
    col4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")
    st.dataframe(df, use_container_width=True, height=300)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv")

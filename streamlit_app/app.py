import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Neobank Analytics", layout="wide")

MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]

@st.cache_resource
def get_connection():
    return duckdb.connect(f"md:neobank?motherduck_token={MOTHERDUCK_TOKEN}")

con = get_connection()

st.title("🏦 Neobank Transaction & Risk Analytics")
st.markdown("Interactive dashboard built with Python, dbt, and MotherDuck.")

tab1, tab2, tab3 = st.tabs(["📊 Executive Overview", "👥 Customer Behavior", "🛡️ Fraud & Risk Control"])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tab1:
    st.header("Executive Overview")
    
    col1, col2, col3 = st.columns(3)
    kpi_data = con.execute("""
        SELECT sum(total_revenue_usd) as revenue, sum(total_transactions) as tx_count, avg(daily_active_users) as dau
        FROM main.mart_executive_daily
        WHERE transaction_date <= '2026-03-31'
    """).fetchdf()
    
    col1.metric("Total Revenue (USD)", f"${kpi_data['revenue'][0]:,.0f}")
    col2.metric("Total Transactions", f"{kpi_data['tx_count'][0]:,.0f}")
    col3.metric("Avg Daily Active Users", f"{kpi_data['dau'][0]:,.0f}")
    
    # TTV Chart (Filtered to stop at March 2026)
    ttv_data = con.execute("""
        SELECT date_trunc('month', transaction_date) as month, sum(total_volume_usd) as volume
        FROM main.mart_executive_daily
        WHERE transaction_date <= '2026-03-31'
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    fig_ttv = px.line(ttv_data, x='month', y='volume', 
                      title="Total Transaction Volume (USD)",
                      labels={'month': 'Date', 'volume': 'Volume (USD)'})
    fig_ttv.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig_ttv, use_container_width=True)

    # Cohort Heatmap
    st.subheader("Cohort Retention Matrix (%)")
    cohort_df = con.execute("""
        SELECT strftime(cohort_month, '%Y-%m') as cohort_month, month_0, month_1, month_2, month_3, month_4, month_5, month_6 
        FROM main.mart_cohort_matrix 
        ORDER BY cohort_month
    """).fetchdf()
    
    cohort_df.columns = ['Cohort', 'Month 0 (Start)', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
    cohort_matrix = cohort_df.set_index('Cohort')
    fig_cohort = px.imshow(cohort_matrix, text_auto=True, aspect="auto", 
                           color_continuous_scale='Blues',
                           labels=dict(x="Month Offset", y="Cohort", color="Retention (%)"))
    st.plotly_chart(fig_cohort, use_container_width=True)

# ==========================================
# TAB 2: CUSTOMER BEHAVIOR
# ==========================================
with tab2:
    st.header("Customer Behavior & Unit Economics")
    
    col1, col2 = st.columns(2)
    
    cat_data = con.execute("SELECT category, sum(total_spend_usd) as spend FROM main.mart_spend_by_category GROUP BY 1 ORDER BY spend DESC").fetchdf()
    fig_pie = px.pie(cat_data, names='category', values='spend', 
                     title="Total Spend (USD) by Category", hole=0.4)
    col1.plotly_chart(fig_pie, use_container_width=True)
    
    seg_data = con.execute("SELECT value_tier, sum(total_spend_usd) as spend FROM main.mart_customer_segmentation GROUP BY 1 ORDER BY spend DESC").fetchdf()
    fig_seg = px.pie(seg_data, names='value_tier', values='spend', 
                     title="Total Spend (USD) by Value Tier", hole=0.4)
    col2.plotly_chart(fig_seg, use_container_width=True)

    st.subheader("Subscription Volume (USD) by Merchant")
    sub_data = con.execute("SELECT merchant, sum(total_subscription_volume_usd) as volume FROM main.mart_subscriptions GROUP BY 1 ORDER BY volume DESC LIMIT 15").fetchdf()
    fig_sub = px.bar(sub_data, x='volume', y='merchant', orientation='h',
                     labels={'merchant': 'Merchant', 'volume': 'Volume (USD)'})
    fig_sub.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
    st.plotly_chart(fig_sub, use_container_width=True)

# ==========================================
# TAB 3: FRAUD & RISK CONTROL
# ==========================================
with tab3:
    st.header("Fraud & Risk Control")
    
    col3, col4 = st.columns(2)
    
    # Stacked Bar Chart: Declined & Blocked (Renamed labels)
    status_data = con.execute("""
        SELECT 
            date_trunc('month', transaction_date) as month, 
            CASE 
                WHEN status = 'Blocked_Fraud' THEN 'Blocked Fraud'
                WHEN status = 'Failed_Insufficient_Funds' THEN 'Insufficient Funds'
                ELSE status 
            END as status_label, 
            sum(transaction_count) as tx_count
        FROM main.mart_fraud_overview
        WHERE status IN ('Blocked_Fraud', 'Failed_Insufficient_Funds')
          AND transaction_date > '2024-09-30'
          AND transaction_date <= '2026-03-31'
        GROUP BY 1, 2 ORDER BY 1
    """).fetchdf()
    
    fig_status = px.bar(status_data, x='month', y='tx_count', color='status_label', barmode='stack',
                        title="Declined & Blocked Transactions (Monthly)",
                        labels={'month': 'Month', 'tx_count': 'Transaction Count', 'status_label': 'Status'},
                        color_discrete_map={'Blocked Fraud': '#D32F2F', 'Insufficient Funds': '#FFA000'})
    fig_status.update_xaxes(tickformat="%Y-%m")
    col3.plotly_chart(fig_status, use_container_width=True)

    # Fraud Rate Trend (Exact same data and color as Lightdash)
    fraud_trend = con.execute("""
        SELECT date_trunc('month', transaction_date) as month, 
               (sum(fraud_transactions)::float / sum(total_transactions)) * 100 as fraud_rate
        FROM main.mart_fraud_rate_trend
        WHERE transaction_date > '2024-09-30' AND transaction_date <= '2026-03-31'
        GROUP BY 1 
        ORDER BY 1
    """).fetchdf()
    
    fig_fraud = px.bar(fraud_trend, x='month', y='fraud_rate', 
                       title="Overall Fraud Rate Trend (%)", 
                       labels={'month': 'Transaction date (Month)', 'fraud_rate': 'Fraud Rate (%)'},
                       text_auto='.2f')
    
    # Set to Dark Blue to match Lightdash
    fig_fraud.update_traces(marker_color='#1E3A8A', textposition='outside')
    fig_fraud.update_xaxes(tickformat="%Y-%m")
    # Add padding for labels
    fig_fraud.update_layout(yaxis_range=[0, max(fraud_trend['fraud_rate']) * 1.2]) 
    col4.plotly_chart(fig_fraud, use_container_width=True)

    st.subheader("Risk Anomalies")
    col5, col6 = st.columns(2)
    
    # Impossible Travel Table
    geo_df = con.execute("""
        SELECT user_id as "User ID", transaction_at as "Transaction Time", amount_usd as "Amount (USD)", 
               user_primary_country as "Home Country", transaction_country as "Transaction Country", 
               minutes_since_last_tx as "Time Since Last Tx", is_fraud_flag as "Fraud Flag"
        FROM main.mart_fraud_geo_anomalies 
        ORDER BY minutes_since_last_tx ASC LIMIT 15
    """).fetchdf()
    col5.markdown("**Impossible Travel (Top 15)**")
    col5.dataframe(geo_df, use_container_width=True, hide_index=True)
    
    # Velocity Anomalies Table
    vel_df = con.execute("""
        SELECT user_id as "User ID", transaction_at as "Transaction Time", amount_usd as "Amount (USD)", 
               tx_count_10min as "Tx Count (10 min)", is_fraud_flag as "Fraud Flag"
        FROM main.mart_fraud_velocity 
        ORDER BY tx_count_10min DESC LIMIT 15
    """).fetchdf()
    col6.markdown("**Velocity Anomalies (Top 15)**")
    col6.dataframe(vel_df, use_container_width=True, hide_index=True)
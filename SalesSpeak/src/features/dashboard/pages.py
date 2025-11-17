import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)


def dashboard_page(sheets_manager, local_db=None):
    """Render the Dashboard page. Uses local DB for real-time analytics."""
    st.markdown("# 🏪 SUPR STORE DASHBOARD / <span style='font-size:18px'>सुपर स्टोर डैशबोर्ड</span>", unsafe_allow_html=True)
    st.markdown("### Sales & Inventory Overview / <span style='font-size:13px'>बिक्री और इन्वेंटरी अवलोकन</span>", unsafe_allow_html=True)

    # Load data from LOCAL DB first (real-time, offline-capable)
    if local_db:
        try:
            sales_list = local_db.get_sales()
            sales_df = pd.DataFrame(sales_list) if sales_list else pd.DataFrame()
        except Exception as e:
            logger.exception("Failed to get sales data from local DB")
            sales_df = pd.DataFrame()

        try:
            inventory_list = local_db.get_inventory()
            inventory_df = pd.DataFrame(inventory_list) if inventory_list else pd.DataFrame()
        except Exception as e:
            logger.exception("Failed to get inventory data from local DB")
            inventory_df = pd.DataFrame()

        try:
            credit_list = local_db.get_credit()
            credit_df = pd.DataFrame(credit_list) if credit_list else pd.DataFrame()
        except Exception as e:
            logger.exception("Failed to get credit data from local DB")
            credit_df = pd.DataFrame()
    else:
        # Fallback to sheets manager if no local DB
        try:
            sales_df = sheets_manager.get_sales_data()
        except Exception as e:
            logger.exception("Failed to get sales data")
            sales_df = pd.DataFrame()

        try:
            inventory_df = sheets_manager.get_inventory_data()
        except Exception as e:
            logger.exception("Failed to get inventory data")
            inventory_df = pd.DataFrame()

        try:
            credit_df = sheets_manager.get_credit_data()
        except Exception as e:
            logger.exception("Failed to get credit data")
            credit_df = pd.DataFrame()

    # Key metrics - medium square cards with rounded edges
    # Defensive parsing for today and numeric values below
    if not sales_df.empty:
        # normalize date column to __date for easier handling
        for c in ['date', 'created_at', 'timestamp']:
            if c in sales_df.columns:
                sales_df['__date'] = pd.to_datetime(sales_df[c], errors='coerce')
                break
        if '__date' not in sales_df.columns:
            sales_df['__date'] = pd.NaT
        # normalize numeric columns
        if 'selling_price' not in sales_df.columns and 'price' in sales_df.columns:
            sales_df['selling_price'] = sales_df['price']
        if 'quantity' not in sales_df.columns and 'qty' in sales_df.columns:
            sales_df['quantity'] = sales_df['qty']
        sales_df['selling_price'] = pd.to_numeric(sales_df.get('selling_price', 0), errors='coerce').fillna(0)
        sales_df['profit'] = pd.to_numeric(sales_df.get('profit', 0), errors='coerce').fillna(0)
        sales_df['quantity'] = pd.to_numeric(sales_df.get('quantity', 0), errors='coerce').fillna(0)

    today = datetime.now().date()
    today_sales = sales_df[sales_df['__date'].dt.date == today] if (not sales_df.empty and '__date' in sales_df.columns) else pd.DataFrame()
    daily_revenue = today_sales['selling_price'].sum() if not today_sales.empty else 0
    daily_profit = today_sales['profit'].sum() if not today_sales.empty else 0
    pending_credit = credit_df[credit_df['status'] == 'Pending']['amount'].astype(float).sum() if not credit_df.empty and 'status' in credit_df.columns else 0
    low_stock_count = 0
    if not inventory_df.empty and 'current_stock' in inventory_df.columns and 'reorder_level' in inventory_df.columns:
        low_stock_count = len(inventory_df[inventory_df['current_stock'].astype(float) < inventory_df['reorder_level'].astype(float)])

    # 4 Cards in 2x2 layout using central .card-style for consistent look
    # Row 1: Today's Sales, Today's Profit
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='card-style card-large'><div style='font-size:16px;'>📅 Today's Sales / <span style='font-size:15px'>आज की बिक्री</span></div><div style='font-size:28px; font-weight:700; margin-top:10px;'>₹{daily_revenue:,.2f}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card-style card-large'><div style='font-size:16px;'>💰 Today's Profit / <span style='font-size:15px'>आज का लाभ</span></div><div style='font-size:28px; font-weight:700; margin-top:10px;'>₹{daily_profit:,.2f}</div></div>", unsafe_allow_html=True)

    # Row 2: Pending Credits, Low Stock Items
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"<div class='card-style card-large'><div style='font-size:16px;'>🤝 Pending Credits / <span style='font-size:15px'>लंबित क्रेडिट</span></div><div style='font-size:28px; font-weight:700; margin-top:10px;'>₹{pending_credit:,.2f}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card-style card-large'><div style='font-size:16px;'>⚠️ Low Stock Items / <span style='font-size:15px'>कम स्टॉक</span></div><div style='font-size:28px; font-weight:700; margin-top:10px;'>{low_stock_count}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Sales Trend (Last 7 Days) / <span style='font-size:13px'>पिछले 7 दिनों की प्रवृत्ति</span>", unsafe_allow_html=True)
        try:
            if not sales_df.empty and '__date' in sales_df.columns and sales_df['__date'].notna().any():
                sales_df_copy = sales_df.copy()
                cutoff = datetime.now() - timedelta(days=7)
                last_7_days = sales_df_copy[sales_df_copy['__date'] >= cutoff]
                if not last_7_days.empty:
                    # group by date only (day resolution)
                    last_7_days['__day'] = last_7_days['__date'].dt.date
                    daily_sales = last_7_days.groupby('__day').agg({
                        'selling_price': 'sum',
                        'profit': 'sum'
                    }).reset_index()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=daily_sales['__day'], y=daily_sales['selling_price'], 
                                             mode='lines+markers', name='Revenue', line=dict(color='deepskyblue')))
                    fig.add_trace(go.Scatter(x=daily_sales['__day'], y=daily_sales['profit'], 
                                             mode='lines+markers', name='Profit', line=dict(color='limegreen')))
                    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='#071024', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("No sales data available yet")
            else:
                st.info("No sales data available yet")
        except Exception as e:
            logger.debug(f"Chart error: {e}")
            st.info("No sales data available yet")

    with col2:
        st.markdown("#### 🏆 Top Selling Items / <span style='font-size:13px'>शीर्ष विक्रय वस्तुएं</span>", unsafe_allow_html=True)
        if not sales_df.empty and 'item_name' in sales_df.columns:
            try:
                # Ensure numeric quantity
                sales_df['quantity'] = pd.to_numeric(sales_df['quantity'], errors='coerce').fillna(0)
                top_items = sales_df.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(5)
                if not top_items.empty:
                    fig = px.bar(x=top_items.values, y=top_items.index, orientation='h',
                                labels={'x': 'Quantity Sold', 'y': 'Item'})
                    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='#071024')
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("No sales data available yet")
            except Exception as e:
                logger.debug(f"Chart error: {e}")
                st.info("No sales data available yet")
        else:
            st.info("No sales data available yet")

    st.markdown("---")

    # Low Stock Alerts
    st.markdown("#### ⚠️ Low Stock Alerts / <span style='font-size:13px'>कम स्टॉक सतर्कता</span>", unsafe_allow_html=True)
    if not inventory_df.empty and 'current_stock' in inventory_df.columns:
        low_stock = inventory_df[inventory_df['current_stock'].astype(float) < inventory_df['reorder_level'].astype(float)]
        if not low_stock.empty:
            display_low = low_stock[['item_name', 'category', 'current_stock', 'reorder_level']].copy()
            display_low.columns = ['Item {वस्तु}', 'Category {श्रेणी}', 'Current Stock {वर्तमान स्टॉक}', 'Reorder Level {पुनः आदेश स्तर}']
            st.dataframe(display_low, width='stretch', hide_index=True)
        else:
            st.success("✅ All items are in stock! {सभी वस्तुएं स्टॉक में हैं}")
    else:
        st.info("No inventory data available yet")

    st.markdown("---")

    # Recent Sales Panel
    st.markdown("#### 📈 Recent Sales / <span style='font-size:13px'>हाल ही की बिक्री</span>", unsafe_allow_html=True)
    if not sales_df.empty:
        try:
            recent_sales = sales_df.tail(10).copy()
            if 'date' in recent_sales.columns:
                recent_sales_display = recent_sales[['date', 'time', 'item_name', 'quantity', 'selling_price', 'profit']].copy()
                recent_sales_display.columns = ['Date {तारीख}', 'Time {समय}', 'Item {वस्तु}', 'Qty {मात्रा}', 'Price {कीमत}', 'Profit {लाभ}']
                recent_sales_display['Price {कीमत}'] = recent_sales_display['Price {कीमत}'].apply(lambda x: f"₹{float(x):.2f}")
                recent_sales_display['Profit {लाभ}'] = recent_sales_display['Profit {लाभ}'].apply(lambda x: f"₹{float(x):.2f}")
                st.dataframe(recent_sales_display, width='stretch', hide_index=True)
            else:
                st.info("No sales data available yet")
        except Exception as e:
            logger.debug(f"Recent sales error: {e}")
            st.info("Error loading recent sales")
    else:
        st.info("No sales recorded yet {कोई विक्रय दर्ज नहीं किया गया}")

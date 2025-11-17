import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from src.core.sheets_manager import SheetsManager
from src.core.database import LocalDB
from src.core.sync_manager import SyncManager
from audiorecorder import audiorecorder
from src.features.sales.pages import sales_entry_page
from src.features.dashboard.pages import dashboard_page

# Page configuration
st.set_page_config(
    page_title="Sales & Inventory Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'sheets_manager' not in st.session_state:
    st.session_state.sheets_manager = SheetsManager()

if 'local_db' not in st.session_state:
    st.session_state.local_db = LocalDB()

if 'sync_manager' not in st.session_state:
    st.session_state.sync_manager = SyncManager(
        st.session_state.local_db,
        st.session_state.sheets_manager
    )

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Sidebar navigation
st.sidebar.title("📊 Sales Management")

pages = {
    "Dashboard": "Dashboard",
    "Sales Entry": "Sales Entry",
    "Credit Ledger": "Credit Ledger",
    "Inventory": "Inventory",
    "Analytics": "Analytics",
    "Reports": "Reports"
}

for page_name, page_key in pages.items():
    if st.sidebar.button(page_name, key=f"nav_{page_key}"):
        st.session_state.current_page = page_key

# Sync status section
st.sidebar.subheader("Sync Status")
sync_status = st.session_state.sync_manager.get_sync_status()

if sync_status["online"]:
    st.sidebar.success("Online")
else:
    st.sidebar.warning("Offline Mode")

if sync_status["unsynced_count"] > 0:
    st.sidebar.info(f"{sync_status['unsynced_count']} records pending sync")

if st.sidebar.button("Sync Now"):
    with st.spinner("Syncing..."):
        result = st.session_state.sync_manager.force_sync()
        if result["success"] or result.get("reason") == "offline":
            st.sidebar.info(f"Sync completed. Online: {st.session_state.sync_manager.is_online}")
        else:
            st.sidebar.error(f"Sync error: {result.get('error', 'Unknown')}")

from src.features.speech_to_text.processor import process_speech_to_text, parse_sales_speech

# Main content based on current page
if st.session_state.current_page == "Dashboard":
    try:
        dashboard_page(st.session_state.sheets_manager, st.session_state.local_db)
    except Exception as e:
        st.error(f"Error loading Dashboard module: {e}")

elif st.session_state.current_page == "Sales Entry":
    # Delegate Sales Entry to modular page with local database
    try:
        sales_entry_page(st.session_state.sheets_manager, st.session_state.local_db)
    except Exception as e:
        st.error(f"Error loading Sales Entry module: {e}")

elif st.session_state.current_page == "Credit Ledger":
    try:
        from src.features.credit_ledger.pages import credit_ledger_page
        credit_ledger_page(st.session_state.sheets_manager, st.session_state.local_db)
    except Exception as e:
        st.error(f"Error loading Credit Ledger module: {e}")

elif st.session_state.current_page == "Inventory":
    try:
        from src.features.inventory.pages import inventory_page
        inventory_page(st.session_state.sheets_manager, st.session_state.local_db)
    except Exception as e:
        st.error(f"Error loading Inventory module: {e}")

elif st.session_state.current_page == "Analytics":
    try:
        from src.features.analytics.pages import analytics_page
        analytics_page(st.session_state.sheets_manager)
    except Exception as e:
        st.error(f"Error loading Analytics module: {e}")

elif st.session_state.current_page == "Reports":
    st.title("📄 Reports")
    
    st.markdown("### 📊 Generate Daily Report")
    
    report_date = st.date_input("Select Date", value=datetime.now())
    
    if st.button("Generate Report", type="primary"):
        sales_df = st.session_state.sheets_manager.get_sales_data()
        
        if not sales_df.empty:
            sales_df['Date'] = pd.to_datetime(sales_df['Date'])
            daily_sales = sales_df[sales_df['Date'] == pd.to_datetime(report_date)]
            
            if not daily_sales.empty:
                st.markdown(f"## Daily Sales Report - {report_date.strftime('%d %B %Y')}")
                st.markdown("---")
                
                # Summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_revenue = daily_sales['Selling Price'].astype(float).sum()
                    st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
                
                with col2:
                    total_profit = daily_sales['Profit'].astype(float).sum()
                    st.metric("Total Profit", f"₹{total_profit:,.2f}")
                
                with col3:
                    total_transactions = len(daily_sales)
                    st.metric("Transactions", total_transactions)
                
                st.markdown("---")
                
                # Payment method breakdown
                st.markdown("### Payment Methods")
                payment_breakdown = daily_sales.groupby('Payment Method')['Selling Price'].sum()
                for method, amount in payment_breakdown.items():
                    st.write(f"**{method}:** ₹{amount:,.2f}")
                
                st.markdown("---")
                
                # Transaction details
                st.markdown("### Transaction Details")
                st.dataframe(daily_sales[['Time', 'Item Name', 'Category', 'Quantity', 
                                         'Selling Price', 'Profit', 'Payment Method']], 
                           use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.info("💡 Use your browser's print function (Ctrl+P) to save this report as PDF")
            else:
                st.warning(f"No sales recorded on {report_date.strftime('%Y-%m-%d')}")
        else:
            st.info("No sales data available.")
    
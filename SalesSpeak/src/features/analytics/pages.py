import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def analytics_page(sheets_manager):
    st.title("📈 Analytics & Insights")
    
    sales_df = sheets_manager.get_sales_data()
    
    if not sales_df.empty:
        # Date range selector
        st.markdown("### 📅 Select Date Range")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("From", value=datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("To", value=datetime.now())
        
        # Filter data
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        filtered_sales = sales_df[(sales_df['Date'] >= pd.to_datetime(start_date)) & 
                                 (sales_df['Date'] <= pd.to_datetime(end_date))]
        
        if not filtered_sales.empty:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = filtered_sales['Selling Price'].astype(float).sum()
                st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
            
            with col2:
                total_profit = filtered_sales['Profit'].astype(float).sum()
                st.metric("Total Profit", f"₹{total_profit:,.2f}")
            
            with col3:
                avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                st.metric("Average Margin", f"{avg_margin:.1f}%")
            
            with col4:
                total_transactions = len(filtered_sales)
                st.metric("Total Transactions", total_transactions)
            
            st.markdown("---")
            
            # Charts
            tab1, tab2, tab3 = st.tabs(["📊 Sales Trend", "💰 Profit Analysis", "📦 Product Performance"])
            
            with tab1:
                daily_stats = filtered_sales.groupby('Date').agg({
                    'Selling Price': 'sum',
                    'Profit': 'sum',
                    'Quantity': 'sum'
                }).reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily_stats['Date'], y=daily_stats['Selling Price'],
                                        mode='lines+markers', name='Revenue', fill='tonexty'))
                fig.add_trace(go.Scatter(x=daily_stats['Date'], y=daily_stats['Profit'],
                                        mode='lines+markers', name='Profit', fill='tonexty'))
                fig.update_layout(title='Daily Sales & Profit Trend', height=400)
                st.plotly_chart(fig, width='stretch')
            
            with tab2:
                category_profit = filtered_sales.groupby('Category').agg({
                    'Profit': 'sum',
                    'Selling Price': 'sum'
                }).reset_index()
                category_profit['Margin %'] = (category_profit['Profit'] / category_profit['Selling Price'] * 100)
                
                fig = px.bar(category_profit, x='Category', y='Profit', 
                            title='Category-wise Profit',
                            color='Margin %', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, width='stretch')
            
            with tab3:
                product_stats = filtered_sales.groupby('Item Name').agg({
                    'Quantity': 'sum',
                    'Selling Price': 'sum',
                    'Profit': 'sum'
                }).reset_index().sort_values('Selling Price', ascending=False).head(10)
                
                fig = px.bar(product_stats, x='Item Name', y='Selling Price',
                            title='Top 10 Products by Revenue',
                            color='Profit', color_continuous_scale='Blues')
                st.plotly_chart(fig, width='stretch')
            
            # Descriptive Analytics
            st.markdown("### 🔍 Descriptive Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Daily Averages")
                num_days = (end_date - start_date).days + 1
                avg_daily_sales = total_revenue / num_days if num_days > 0 else 0
                avg_daily_profit = total_profit / num_days if num_days > 0 else 0
                avg_daily_transactions = total_transactions / num_days if num_days > 0 else 0
                
                st.write(f"**Average Daily Sales:** ₹{avg_daily_sales:,.2f}")
                st.write(f"**Average Daily Profit:** ₹{avg_daily_profit:,.2f}")
                st.write(f"**Average Daily Transactions:** {avg_daily_transactions:.1f}")
            
            with col2:
                st.markdown("#### Best Performance")
                best_day = daily_stats.loc[daily_stats['Selling Price'].idxmax()]
                st.write(f"**Best Sales Day:** {best_day['Date'].strftime('%Y-%m-%d')}")
                st.write(f"**Revenue:** ₹{best_day['Selling Price']:,.2f}")
                st.write(f"**Profit:** ₹{best_day['Profit']:,.2f}")
        
        else:
            st.info("No data available for selected date range.")
    
    else:
        st.info("No sales data available. Start recording sales to see analytics!")

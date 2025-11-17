import streamlit as st
import plotly.express as px
import pandas as pd


def inventory_page(sheets_manager, local_db=None):
    st.markdown("# 📦 Inventory & Purchase Entry / <span style='font-size:11px'>इन्वेंटरी और खरीदारी प्रविष्टि</span>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["View Inventory / इन्वेंटरी देखें", "Add Purchase / खरीदारी जोड़ें"])
    
    with tab1:
        # Get inventory from local database (offline-capable)
        if local_db:
            inventory_list = local_db.get_inventory()
            
            if inventory_list:
                inventory_df = pd.DataFrame(inventory_list)
                
                # Summary
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_items = len(inventory_df)
                    st.metric("Total Items / कुल आइटम", total_items)
                
                with col2:
                    total_value = (inventory_df['current_stock'].astype(float) * inventory_df['selling_price'].astype(float)).sum()
                    st.metric("Inventory Value / सूची मूल्य", f"₹{total_value:,.2f}")
                
                with col3:
                    low_stock = len(inventory_df[inventory_df['current_stock'].astype(float) < inventory_df['reorder_level'].astype(float)])
                    st.metric("Low Stock Items / कम स्टॉक आइटम", low_stock)
                
                with col4:
                    out_of_stock = len(inventory_df[inventory_df['current_stock'].astype(float) <= 0])
                    st.metric("Out of Stock / स्टॉक खत्म", out_of_stock)
                
                st.markdown("---")
                
                # Filters
                col1, col2 = st.columns(2)
                
                with col1:
                    category_filter = st.multiselect("Filter by Category / श्रेणी द्वारा फ़िल्टर करें", 
                                                    options=inventory_df['category'].unique().tolist())
                
                with col2:
                    stock_status = st.selectbox("Stock Status / स्टॉक स्थिति", ["All", "Low Stock", "Out of Stock", "In Stock"])
                
                # Apply filters
                if category_filter:
                    filtered_df = inventory_df[inventory_df['category'].isin(category_filter)].copy()
                else:
                    filtered_df = inventory_df.copy()
                
                if stock_status == "Low Stock":
                    filtered_df = filtered_df[filtered_df['current_stock'].astype(float) < filtered_df['reorder_level'].astype(float)]
                elif stock_status == "Out of Stock":
                    filtered_df = filtered_df[filtered_df['current_stock'].astype(float) <= 0]
                elif stock_status == "In Stock":
                    filtered_df = filtered_df[filtered_df['current_stock'].astype(float) > 0]
                
                # Display table
                if not filtered_df.empty:
                    display_df = filtered_df[['item_name', 'category', 'current_stock', 'cost_price', 'selling_price', 'reorder_level']].copy()
                    display_df.columns = ['Item / वस्तु', 'Category / श्रेणी', 'Current Stock / वर्तमान स्टॉक', 'Cost Price / लागत', 'Selling Price / बिक्री मूल्य', 'Reorder Level / पुनः आदेश स्तर']
                    st.dataframe(display_df, width='stretch', hide_index=True)
                else:
                    st.info("No items match the selected filters.")
                
                # Category-wise stock value
                st.markdown("### 📊 Category-wise Stock Value / श्रेणी के अनुसार स्टॉक मूल्य")
                category_value = inventory_df.groupby('category').apply(
                    lambda x: (x['current_stock'].astype(float) * x['selling_price'].astype(float)).sum()
                ).reset_index(name='Value')
                
                fig = px.pie(category_value, values='Value', names='category', title='Stock Value by Category')
                st.plotly_chart(fig, width='stretch')
                
            else:
                st.info("No inventory data available yet.")
        else:
            st.error("Local database not available.")
    
    with tab2:
        st.subheader("➕ Add Purchase / खरीदारी जोड़ें")
        st.info("💡 Enter total cost of purchase, selling price per unit, and quantity. Cost per unit will be calculated automatically.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<p style='font-size: 18px;'>Item Name / वस्तु का नाम</p>", unsafe_allow_html=True)
            item_name = st.text_input("Item Name*", label_visibility="collapsed", help="Name of the product")
            
            st.markdown("<p style='font-size: 18px;'>Category / श्रेणी</p>", unsafe_allow_html=True)
            # More comprehensive kirana categories
            category = st.selectbox("Category", [
                "Spices & Masala",
                "Grains & Pulses",
                "Dairy & Eggs",
                "Beverages",
                "Snacks & Namkeen",
                "Bakery",
                "Household",
                "Personal Care",
                "Stationery",
                "Others"
            ], label_visibility="collapsed")
            
            st.markdown("<p style='font-size: 18px;'>Quantity Purchased / खरीदी गई मात्रा</p>", unsafe_allow_html=True)
            quantity_change = st.number_input("Quantity Purchased*", label_visibility="collapsed", value=None, step=1, help="Number of units purchased", min_value=1)
        
        with col2:
            st.markdown("<p style='font-size: 18px;'>Total Cost (₹) / कुल लागत</p>", unsafe_allow_html=True)
            # Use an integer-style display if placeholder unsupported; keep decimals if user enters them
            total_cost = st.number_input("Total Cost (₹)*", label_visibility="collapsed", min_value=0.0, format="%.0f", placeholder="0", help="Total amount paid for all units")
            
            st.markdown("<p style='font-size: 18px;'>Selling Price per Unit (₹) / प्रति यूनिट बिक्री मूल्य</p>", unsafe_allow_html=True)
            selling_price = st.number_input("Selling Price per Unit (₹)*", label_visibility="collapsed", min_value=0.0, format="%.0f", placeholder="0", step=1.0, help="What customers pay per unit")
        
        # Calculate cost per unit from total cost
        cost_per_unit = total_cost / quantity_change if quantity_change and quantity_change > 0 else 0.0
        
        if cost_per_unit > 0:
            st.success(f"✅ Cost per unit: ₹{cost_per_unit:.2f}")
        
        # Place the add button to the right in a smaller column so it doesn't span whole row
        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col2:
            if st.button("✅ Add Purchase / खरीदारी जोड़ें"):
                if item_name and total_cost > 0 and selling_price > 0 and quantity_change and quantity_change > 0:
                    if local_db:
                        success = local_db.add_or_update_inventory(
                        item_name=item_name.strip(),  # Normalize case
                        category=category,
                        quantity_change=quantity_change,
                        cost_price=cost_per_unit,
                        selling_price=selling_price
                    )
                    
                    if success:
                        st.success(f"✅ Purchase added: {item_name} ({quantity_change} units @ ₹{cost_per_unit:.2f}/unit)")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add purchase.")
                else:
                    st.error("❌ Local database not available.")
            else:
                st.error("⚠️ Please fill: Item Name, Total Cost, Selling Price, and Quantity")

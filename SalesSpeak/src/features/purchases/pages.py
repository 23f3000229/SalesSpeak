import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def purchases_page(sheets_manager, local_db=None):
    st.title("🛒 Purchase Entry")
    st.markdown("### Add New Purchase")
    
    col1, col2 = st.columns(2)
    
    with col1:
        slip_number = st.text_input("Slip Number*", help="Invoice or receipt number")
        item_name_purchase = st.text_input("Item Name*", placeholder="e.g. Aata / Maida")
        category_purchase = st.selectbox("Category*", 
                                        [
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
                                        ],
                                        key="purchase_category")
        quantity_purchase = st.number_input("Quantity*", min_value=1, value=1, step=1, key="purchase_qty")
        unit_purchase = st.selectbox("Unit*", ["Kg", "Gram", "Liter", "ML", "Piece", "Pack", "Box"], key="purchase_unit")
        total_price_purchase = st.number_input("Total Price (₹)*", min_value=0.0, format="%.0f", placeholder="0", step=0.1, key="purchase_total")
    
    with col2:
        supplier_purchase = st.text_input("Supplier*")
        has_expiry = st.checkbox("Has Expiry Date", key="has_expiry_check")
        if has_expiry:
            expiry_date_purchase = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=30), key="purchase_expiry")
        else:
            expiry_date_purchase = None
        selling_price_purchase = st.number_input("Selling Price (₹)*", min_value=0.0, format="%.0f", placeholder="0", step=0.1, 
                      help="Price per unit for selling", key="purchase_selling")
        notes_purchase = st.text_area("Notes (Optional)", key="purchase_notes")
        
        # Show cost per unit
        if quantity_purchase > 0 and total_price_purchase > 0:
            cost_per_unit = total_price_purchase / quantity_purchase
            st.metric("Cost per Unit", f"₹{cost_per_unit:.2f}")
    
    if st.button("💾 Save Purchase", type="primary"):
        if slip_number and item_name_purchase and category_purchase and quantity_purchase > 0 and total_price_purchase > 0 and supplier_purchase and selling_price_purchase > 0:
            expiry_str = expiry_date_purchase.strftime('%Y-%m-%d') if expiry_date_purchase else ''
            
            if local_db:
                success = local_db.add_purchase(
                    slip_number=slip_number,
                    item_name=item_name_purchase,
                    category=category_purchase,
                    quantity=quantity_purchase,
                    unit=unit_purchase,
                    total_price=total_price_purchase,
                    supplier=supplier_purchase,
                    expiry_date=expiry_str,
                    selling_price=selling_price_purchase,
                    notes=notes_purchase
                )
                
                if success:
                    st.success(f"✅ Purchase saved locally! {quantity_purchase} {unit_purchase} of {item_name_purchase} added.")
                    st.rerun()
                else:
                    st.error("Failed to save purchase to local database.")
            else:
                st.error("Local database not available.")
        else:
            st.error("Please fill all required fields marked with *")
    
    st.markdown("---")
    
    # View recent purchases from local database
    if local_db:
        st.markdown("### Recent Purchases")
        purchases_list = local_db.get_purchases(limit=10)
        
        if purchases_list:
            purchases_df = pd.DataFrame(purchases_list)
            display_df = purchases_df[['date', 'slip_number', 'item_name', 'quantity', 'unit', 'total_price', 'supplier']].copy()
            display_df.columns = ['Date', 'Slip #', 'Item', 'Qty', 'Unit', 'Total Price', 'Supplier']
            st.dataframe(display_df, width='stretch', hide_index=True)
        else:
            st.info("No purchase records yet.")
    else:
        st.error("Local database not available.")

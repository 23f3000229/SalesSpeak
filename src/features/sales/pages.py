import streamlit as st
from datetime import datetime


def sales_entry_page(sheets_manager, local_db=None):
    """Render Sales Entry UI with offline-first local storage - supports multiple items in cart."""
    st.markdown("# 💰 Sales Entry / <span style='font-size:11px'>बिक्री प्रविष्टि</span>", unsafe_allow_html=True)
    st.markdown("### ✍️ Record a Sale / <span style='font-size:11px'>विक्रय रिकॉर्ड करें</span>", unsafe_allow_html=True)

    # Initialize session state for cart
    if "sale_items" not in st.session_state:
        st.session_state.sale_items = []
    if "payment_method" not in st.session_state:
        st.session_state.payment_method = "Cash"

    # Get inventory for lookups
    inventory_list = []
    if local_db:
        inventory_list = local_db.get_inventory()

    # Button styling is handled centrally by theme module

    # Input row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<p style='font-size:16px;'>Item Name / वस्तु का नाम</p>", unsafe_allow_html=True)
        inventory_names = [i.get('item_name', '') for i in inventory_list] if inventory_list else []
        # Make selectbox default to an empty placeholder option so no item is pre-selected
        if inventory_names:
            options = [""] + inventory_names
            selected_item = st.selectbox("Item Name*", options=options, key="item_select", label_visibility="collapsed")
            if selected_item == "":
                item_name = st.text_input("Item Name / वस्तु का नाम", key="item_sales_text", placeholder="Type or select item", label_visibility="collapsed")
            else:
                item_name = selected_item
        else:
            item_name = st.text_input("Item Name*", key="item_sales", label_visibility="collapsed", placeholder="Type item name")

    with col2:
        st.markdown("<p style='font-size:16px;'>Quantity / मात्रा</p>", unsafe_allow_html=True)
        quantity = st.number_input("Quantity*", min_value=1, value=1, step=1, key="qty_sales", label_visibility="collapsed")

    with col3:
        st.markdown("<p style='font-size:16px;'>Total Amount (₹) / कुल राशि</p>", unsafe_allow_html=True)
        # Auto-calculate total amount from inventory selling price
        selling_price_per_unit = 0.0
        cost_price = 0.0
        inventory_item_name = ""
        if item_name and local_db:
            for item in inventory_list:
                if item.get('item_name', '').lower() == str(item_name).lower():
                    selling_price_per_unit = float(item.get('selling_price', 0.0))
                    cost_price = float(item.get('cost_price', 0.0))
                    inventory_item_name = item.get('item_name', '')
                    break

        total_amount = selling_price_per_unit * quantity
        # Display total amount highlighted (darker color)
        st.markdown(f"<div style='background-color: #2E8B57; padding: 10px; border-radius: 8px; text-align: center;'><span style='font-size: 20px; color: white; font-weight: 700;'>₹{total_amount:.2f}</span></div>", unsafe_allow_html=True)

    # Add item to cart
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("➕ Add Item to Cart / कार्ट में जोड़ें", key="add_item_btn"):
            if (item_name or inventory_item_name) and quantity > 0:
                st.session_state.sale_items.append({
                    "item_name": inventory_item_name if inventory_item_name else item_name,
                    "quantity": quantity,
                    "selling_price": selling_price_per_unit,
                    "cost_price": cost_price,
                    "total_amount": total_amount
                })
                st.success(f"✅ Added {inventory_item_name or item_name} x{quantity} to cart")
                st.rerun()
            else:
                st.error("⚠️ Please select a valid item with quantity")

    with col_btn2:
        # Clear cart button (styled via CSS above)
        if st.button("🗑️ Clear Cart / कार्ट साफ करें", key="clear_cart_btn"):
            st.session_state.sale_items = []
            st.rerun()

    # Display cart
    if st.session_state.sale_items:
        st.markdown("---")
        st.subheader("🛒 Cart Items / कार्ट वस्तुएं")

        cart_data = []
        total_sale_amount = 0.0
        total_profit = 0.0

        for idx, item in enumerate(st.session_state.sale_items):
            cart_data.append({
                "Item / वस्तु": item['item_name'],
                "Qty / मात्रा": item['quantity'],
                "Price / कीमत": f"₹{item['selling_price']:.2f}",
                "Total / कुल": f"₹{item['total_amount']:.2f}"
            })
            total_sale_amount += item['total_amount']
            profit = (item['selling_price'] - item['cost_price']) * item['quantity']
            total_profit += profit

        # Show totals (cards)
        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.markdown(f"<div style='background-color: #1E90FF; padding: 16px; border-radius: 8px; text-align:center; color: white;'><div style='font-size:14px;'>Total Sale</div><div style='font-size:20px; font-weight:700;'>₹{total_sale_amount:.2f}</div></div>", unsafe_allow_html=True)
        with col_tot2:
            st.markdown(f"<div style='background-color: #FF1493; padding: 16px; border-radius: 8px; text-align:center; color: white;'><div style='font-size:14px;'>Total Profit</div><div style='font-size:20px; font-weight:700;'>₹{total_profit:.2f}</div></div>", unsafe_allow_html=True)

        st.dataframe(cart_data, width='stretch', hide_index=True)

        st.markdown("---")

        # Payment method - only Cash and UPI
        st.markdown("<p style='font-size:16px;'>Payment Method / भुगतान विधि</p>", unsafe_allow_html=True)
        payment_method = st.selectbox("Payment Method", ["Cash", "UPI"], key="pm_sales", label_visibility="collapsed")
        st.session_state.payment_method = payment_method

        st.markdown("<p style='font-size:16px;'>Notes (optional) / नोट्स</p>", unsafe_allow_html=True)
        notes = st.text_area("Notes", height=60, label_visibility="collapsed")

        # Complete sale button
        if st.button("💾 Complete Sale / बिक्री पूरी करें", key="complete_sale_btn"):
            if local_db and len(st.session_state.sale_items) > 0:
                all_success = True
                for item in st.session_state.sale_items:
                    success = local_db.add_sale(
                        item_name=item['item_name'],
                        category="",
                        quantity=item['quantity'],
                        cost_price=item['cost_price'],
                        selling_price=item['selling_price'],
                        payment_method=payment_method,
                        notes=notes
                    )
                    if not success:
                        all_success = False

                if all_success:
                    st.success("✅ Sale recorded")
                    st.session_state.sale_items = []
                    st.rerun()
                else:
                    st.error("❌ Failed to save some items. Please try again.")
            else:
                st.error("❌ No items in cart or database not available.")

    # Recent sales panel
    st.markdown("---")
    st.subheader("📊 Recent Sales / हाल ही के विक्रय")
    if local_db:
        sales = local_db.get_sales(limit=10)
        if sales:
                st.dataframe(
                [{
                    "Date / तारीख": s.get("date", ""),
                    "Time / समय": s.get("time", ""),
                    "Item / वस्तु": s.get("item_name", ""),
                    "Qty / मात्रा": s.get("quantity", 0),
                    "Price / कीमत": f"₹{s.get('selling_price', 0):.2f}",
                    "Profit / लाभ": f"₹{s.get('profit', 0):.2f}",
                    "Status / स्थिति": "✅ Synced" if s.get("synced") else "⏳ Pending"
                } for s in sales],
                width='stretch',
                hide_index=True
            )
        else:
            st.info("No sales recorded yet.")
    else:
        st.info("Local database not available.")

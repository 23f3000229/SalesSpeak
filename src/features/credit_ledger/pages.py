import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time


def credit_ledger_page(sheets_manager, local_db=None):
    # Title with small Hindi text after slash
    st.markdown("# 🤝 Credit Ledger / <span style='font-size:11px'>उधार खाता</span>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Add Credit Sale / क्रेडिट जोड़ें", "📋 View Credits / क्रेडिट देखें"])
    
    with tab1:
        st.markdown("### Add New Credit Sale / <span style='font-size:11px'>नया क्रेडिट जोड़ें</span>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<p style='font-size:18px;'>Customer Name / ग्राहक का नाम</p>", unsafe_allow_html=True)
            customer_name = st.text_input("Customer Name*", key="cn_credit", label_visibility="collapsed")
            st.markdown("<p style='font-size:18px;'>Phone Number / फ़ोन नंबर</p>", unsafe_allow_html=True)
            phone = st.text_input("Phone Number*", key="ph_credit", label_visibility="collapsed")
            st.markdown("<p style='font-size:18px;'>Item Name / वस्तु का नाम</p>", unsafe_allow_html=True)
            item_name_credit = st.text_input("Item Name (Optional)", key="item_credit", label_visibility="collapsed", placeholder="Optional")
            st.markdown("<p style='font-size:18px;'>Credit Amount / क्रेडिट राशि</p>", unsafe_allow_html=True)
            # Use single-digit display when empty; placeholder text shown where supported
            amount = st.number_input("Credit Amount (₹)*", min_value=0.0, format="%.0f", step=1.0, key="amt_credit", label_visibility="collapsed")
        
        with col2:
            st.markdown("<p style='font-size:18px;'>Due Date / देय तिथि</p>", unsafe_allow_html=True)
            due_date = st.date_input("Due Date*", value=datetime.now() + timedelta(days=7), key="dd_credit", label_visibility="collapsed")
            st.markdown("<p style='font-size:18px;'>Notes / नोट्स</p>", unsafe_allow_html=True)
            notes = st.text_area("Notes", key="notes_credit", height=100, label_visibility="collapsed")
        
        if st.button("💾 Save Credit Sale / क्रेडिट सहेजें", type="primary"):
            if customer_name and phone and amount and amount > 0:
                if local_db:
                    success = local_db.add_credit_sale(
                        customer_name=customer_name,
                        phone=phone,
                        item_name=item_name_credit if item_name_credit else None,
                        amount=amount,
                        due_date=due_date.strftime('%Y-%m-%d'),
                        notes=notes
                    )
                    if success:
                        # show a short success message then pause briefly before rerun
                        st.success("✅ Credit sale saved locally!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to save credit sale to local database.")
                else:
                    st.error("Local database not available.")
            else:
                st.error("Please fill all required fields.")
    
    with tab2:
        st.markdown("### Credit Records / <span style='font-size:11px'>क्रेडिट रिकॉर्ड</span>", unsafe_allow_html=True)
        
        if local_db:
            credit_list = local_db.get_credit()
            
            if credit_list:
                credit_df = pd.DataFrame(credit_list)
                
                # Filter out paid credits for display
                active_credits = credit_df[credit_df['status'] != 'Paid']
                paid_credits = credit_df[credit_df['status'] == 'Paid']
                
                # Summary metrics (removed Partial Paid - not used)
                col1, col2 = st.columns(2)

                with col1:
                    total_credit = credit_df['amount'].astype(float).sum()
                    st.metric("Total Credits (All-time) / कुल क्रेडिट", f"₹{total_credit:,.2f}")

                with col2:
                    pending_credit = credit_df[credit_df['status'] == 'Pending']['amount'].astype(float).sum()
                    st.metric("Pending / लंबित", f"₹{pending_credit:,.2f}")
                
                st.markdown("---")
                
                # Show active credits
                st.markdown("### 📊 Active Credits")
                if not active_credits.empty:
                    display_cols = ['date', 'customer_name', 'phone', 'item_name', 'amount', 'due_date', 'status']
                    display_df = active_credits[[col for col in display_cols if col in active_credits.columns]].copy()
                    display_df.columns = ['Date', 'Customer', 'Phone', 'Item', 'Amount', 'Due Date', 'Status']
                    st.dataframe(display_df, width='stretch', hide_index=True)
                else:
                    st.success("✅ No pending or partial credits!")
                
                # Update status section
                st.markdown("---")
                st.markdown("### Update Payment Status")
                
                if not active_credits.empty:
                    # Create list of only active credits
                    credit_options = []
                    for _, row in active_credits.iterrows():
                        credit_options.append({
                            'display': f"{row['customer_name']} - ₹{row['amount']} ({row['status']})",
                            'id': row['id'],
                            'current_status': row['status'],
                            'current_amount': row['amount']
                        })
                    
                    option_display = [opt['display'] for opt in credit_options]
                    selected_option = st.selectbox(
                        "Select Credit Record to Update",
                        options=option_display,
                        key="credit_select",
                        label_visibility="collapsed"
                    )
                    
                    # Get the selected credit info
                    selected_credit = next(opt for opt in credit_options if opt['display'] == selected_option)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Only allow Pending or Paid statuses now
                        new_status = st.selectbox("New Status", ["Pending", "Paid"], index=0)

                    with col2:
                        partial_amount = None
                    
                    with col3:
                        st.write("")
                        st.write("")
                        if st.button("✅ Update"):
                            if local_db.update_credit_status(selected_credit['id'], new_status):
                                st.success(f"✅ Status updated to {new_status}")
                                st.rerun()
                            else:
                                st.error("Failed to update status.")
                else:
                    st.info("No pending or partial credits to update.")
                
                # Show paid credits history
                    if not paid_credits.empty:
                        with st.expander("📜 Paid Credits History"):
                            display_cols = ['date', 'customer_name', 'amount', 'due_date']
                            display_df = paid_credits[[col for col in display_cols if col in paid_credits.columns]].copy()
                            display_df.columns = ['Date', 'Customer', 'Amount', 'Due Date']
                            st.dataframe(display_df, width='stretch', hide_index=True)
            else:
                st.info("No credit records yet.")
        else:
            st.error("Local database not available.")

# SalesSpeak - Quick Reference Guide

## 🚀 Quick Start

### 1. Run the App
```bash
streamlit run app.py
```
App opens at: `http://localhost:8501`

---

## 📱 Main Features

### 💰 Sales Entry
- **Enter**: Item name, Quantity, Selling price, Payment method
- **Auto-calculated**: Cost price (from inventory), Profit
- **Formula**: Profit = (Selling Price - Cost Price) × Quantity
- **Storage**: Saves locally, syncs to Google Sheets when online

### 📦 Inventory Management
- **Add items**: Name, Category, Cost Price, Selling Price, Reorder Level
- **Track stock**: Add/remove quantities (goes negative if over-sold)
- **Alerts**: Low stock items, Out of stock items
- **View**: Category-wise stock value pie chart

### 💳 Credit Ledger
- **Record credit**: Customer name, phone, item, amount, due date
- **Track payment**: Status = Pending or Paid
- **Syncs**: To Google Sheets for follow-up

### 📊 Dashboard
- **Real-time KPIs**: Total sales, profit, inventory value
- **Alerts**: Low stock, out of stock items
- **Charts**: Sales by payment method, category performance
- **Title**: 🏪 SUPR STORE DASHBOARD

---

## 🔧 Settings & Controls

### Sidebar Controls
1. **Manual Sync** - Force sync to Google Sheets immediately
2. **Sync Status** - Shows "Online" or "Offline"
3. **Last Synced** - Timestamp of last sync

### Database
- **Location**: `sales_data.db` (SQLite)
- **Backup**: Automatically synced to Google Sheets
- **Tables**: sales, inventory, credit, purchases, sync_log

---

## 📊 Data Structure

### Sales Table
| Field | Type | Description |
|-------|------|-------------|
| date | Text | YYYY-MM-DD |
| time | Text | HH:MM:SS |
| item_name | Text | Product name |
| quantity | Integer | Units sold |
| cost_price | Real | Cost per unit |
| selling_price | Real | Price per unit |
| profit | Real | (selling - cost) × qty |
| payment_method | Text | Cash/Card/UPI/Cheque |
| status | Integer | 0=Pending, 1=Synced |

### Inventory Table
| Field | Type | Description |
|-------|------|-------------|
| item_name | Text | Product name (UNIQUE) |
| category | Text | Food/Beverage/Snacks/Others |
| current_stock | Integer | Current quantity (can be negative) |
| cost_price | Real | Cost per unit |
| selling_price | Real | Selling price per unit |
| reorder_level | Integer | Alert threshold |
| status | Integer | 0=Pending, 1=Synced |

### Credit Table
| Field | Type | Description |
|-------|------|-------------|
| date | Text | YYYY-MM-DD |
| customer_name | Text | Customer name |
| phone | Text | Phone number |
| item_name | Text | Item purchased on credit |
| amount | Real | Credit amount |
| due_date | Text | Payment due date |
| status | Text | Pending or Paid |
| synced | Integer | 0=Pending, 1=Synced |

---

## 🌐 Google Sheets Setup

### Quick Steps
1. Create Google Cloud project and service account
2. Download JSON key file
3. Place in project root as `google_service_account.json`
4. Create Google Sheet and share with service account email
5. Restart app and check sidebar for sync status

### For Detailed Steps
→ Read `GOOGLE_SHEETS_SETUP.md` in project root

---

## 🐛 Troubleshooting

### App won't start
- Check Python 3.11+: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check for errors in terminal

### Data not syncing
- Click **Manual Sync** in sidebar
- Check sync status shows "Online"
- Verify Google Sheet is shared with service account
- Check `sync_log` tab in Google Sheet for errors

### Profit showing as just selling price
- Make sure item exists in Inventory with cost price
- Re-enter the sale to pull latest cost from inventory
- Check database: Sales table has non-zero `cost_price`

### Out of stock not showing
- Go to Inventory
- Filter by "Out of Stock" status
- Should show items where current_stock ≤ 0

---

## 📈 Business Metrics

### Daily Metrics (from Dashboard)
- **Total Sales Today**: Sum of selling_price × qty
- **Total Profit Today**: Sum of profit for all sales
- **Number of Transactions**: Count of sales entries

### Inventory Metrics
- **Inventory Value**: Sum of current_stock × cost_price
- **Low Stock Items**: Count where current_stock < reorder_level
- **Out of Stock Items**: Count where current_stock ≤ 0

### Credit Metrics
- **Outstanding Credit**: Sum where status = "Pending"
- **Paid Credit**: Sum where status = "Paid"
- **Total Credit Given**: Outstanding + Paid

---

## 💡 Best Practices

### Data Entry
✅ Use consistent item names (e.g., "Alloo Paratha", not "Aloo")  
✅ Update inventory first before recording sales  
✅ Enter credit due date realistically  
✅ Use payment method accurately (affects reporting)  

### Regular Maintenance
✅ Review "Out of Stock" items daily  
✅ Check "Low Stock" items and reorder  
✅ Follow up on "Pending" credits weekly  
✅ Review Dashboard daily for trends  

### Cloud Backup
✅ Check sync status in sidebar (should be "Online")  
✅ Click **Manual Sync** weekly to force sync  
✅ Review Google Sheet monthly for backup  
✅ Keep JSON key file secure (don't share)  

---

## 🔐 Security

### Protect Your Data
- Keep `google_service_account.json` private
- Don't commit to GitHub (add to `.gitignore`)
- Back up `sales_data.db` regularly
- Use strong Google account password

### If JSON Key Compromised
1. Go to Google Cloud Console
2. Delete the old key from Service Account → KEYS
3. Create a new key and download it
4. Replace the old `google_service_account.json` file
5. Restart app

---

## 📞 Support Information

### Check These First
1. Read error message in app
2. Check browser console (F12 → Console tab)
3. Look at sync_log in Google Sheet
4. Review terminal output for Python errors

### Common Issues
- "Authentication failed" → Check JSON file exists and is valid
- "Permission denied" → Share Google Sheet with service account
- "Out of memory" → Restart app
- "Sync not working" → Click Manual Sync, check internet

---

## 🎯 Next Steps

1. ✅ Test all features with sample data
2. ✅ Set up Google Sheets using guide
3. ✅ Back up `sales_data.db` file
4. ✅ Review Dashboard daily
5. ✅ Export to Google Sheets for analysis

---

**Version**: 1.0  
**Last Updated**: 2025  
**For Full Documentation**: See IMPROVEMENTS_SUMMARY.md and GOOGLE_SHEETS_SETUP.md

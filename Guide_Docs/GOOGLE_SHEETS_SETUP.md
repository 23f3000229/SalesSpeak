# Google Sheets Integration Setup Guide for SalesSpeak

This guide walks you through setting up Google Sheets integration for cloud backup and data analysis of your SalesSpeak store data.

## Overview

SalesSpeak uses a **hybrid approach**:
- **Local Storage**: SQLite database stores all sales/inventory/credit data locally on your device (works offline)
- **Cloud Backup**: Google Sheets stores a copy of your data for backup, analysis, and sharing
- **Automatic Sync**: When online, new records automatically sync to Google Sheets

## Step-by-Step Setup Instructions

### Phase 1: Create a Google Cloud Project

1. **Open Google Cloud Console**
   - Go to https://console.cloud.google.com/
   - Sign in with your Google account (personal or business)

2. **Create a New Project**
   - Click the **Project** dropdown at the top
   - Click **NEW PROJECT**
   - Enter project name: `SalesSpeak` (or your preference)
   - Click **CREATE**
   - Wait 2-3 minutes for the project to be created

3. **Enable Google Sheets API**
   - In the left menu, go to **APIs & Services** → **Library**
   - Search for **Google Sheets API**
   - Click on it
   - Click **ENABLE**

4. **Create a Service Account**
   - Go to **APIs & Services** → **Credentials**
   - Click **+ CREATE CREDENTIALS** at the top
   - Select **Service Account**
   - Fill in the form:
     - Service account name: `SalesSpeak Bot` (or your preference)
     - Service account ID: Auto-filled (keep as is)
     - Click **CREATE AND CONTINUE**
   - Grant basic role (optional): Skip this for now
   - Click **CONTINUE** → **DONE**

5. **Create and Download the Service Account Key**
   - In the Credentials page, find your service account under **Service Accounts**
   - Click on the email (looks like `salespeak-bot@project-name.iam.gserviceaccount.com`)
   - Go to the **KEYS** tab
   - Click **ADD KEY** → **Create new key**
   - Choose **JSON** format
   - Click **CREATE**
   - A JSON file will download automatically (save it safely!)
   - Rename it to `google_service_account.json` for clarity

### Phase 2: Set Up Google Sheet for Data Storage

1. **Create a Google Sheet**
   - Go to https://sheets.google.com/
   - Click **+ Blank** to create a new spreadsheet
   - Name it: `SalesSpeak Data Backup`

2. **Share the Sheet with Service Account**
   - Open the JSON file you downloaded
   - Find the email field (looks like `salespeak-bot@project-name.iam.gserviceaccount.com`)
   - Copy this email
   - In your Google Sheet, click **Share** (top right)
   - Paste the email
   - Give **Editor** permission (so the bot can write data)
   - Click **Share**

3. **Sheet Structure** (Auto-created by SalesSpeak)
   - When you first sync, SalesSpeak will create these sheets automatically:
     - **sales**: Item name, date, time, quantity, selling price, profit, payment method
     - **inventory**: Item name, category, current stock, cost price, selling price, reorder level
     - **credit**: Customer name, phone, item, amount, due date, payment status
     - **purchases** (optional): Purchase records and supplier info

### Phase 3: Connect SalesSpeak to Google Sheets

#### Option A: Using Replit Connector (Recommended for Replit users)
*Skip this if you're running locally*

1. If you're using Replit:
   - Go to **Secrets** (left sidebar, lock icon)
   - Add new secret:
     - Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
     - Value: Copy the entire contents of your `google_service_account.json` file
   - Save
   - SalesSpeak will auto-detect and use this

#### Option B: Using Local File (For Desktop/Local Installation)

1. **Place the JSON File**
   - Copy your `google_service_account.json` file
   - Place it in the SalesSpeak project root directory (same level as `app.py`)
   
   ```
   SalesSpeak/
   ├── app.py
   ├── google_service_account.json  ← Put it here
   ├── sheets_manager.py
   └── ... other files
   ```

2. **Configure Environment Variable (Optional)**
   - Create a `.env` file in the project root:
   ```
   GOOGLE_SERVICE_ACCOUNT_JSON_PATH=google_service_account.json
   ```

3. **Restart the App**
   - Run `streamlit run app.py`
   - The app will detect the JSON file and initialize Google Sheets

### Phase 4: Test the Integration

1. **Check the Dashboard**
   - Open SalesSpeak in your browser
   - Go to the **Dashboard** tab
   - If setup is correct, you should see a message about sync status

2. **Add Test Data**
   - Go to **Sales Entry** and add a test sale
   - Go to **Inventory** and add a test item
   - Go to **Credit Ledger** and add a test credit

3. **Check Google Sheet**
   - Open your Google Sheet in browser
   - You should see the sheets created:
     - **sales** tab with your test sale
     - **inventory** tab with your test item
     - **credit** tab with your test credit
   - The **sync_log** tab tracks what was synced

4. **Verify Sync Status**
   - In SalesSpeak, open the sidebar
   - Click **Manual Sync** button
   - Watch the sync log for any errors
   - Go back to Google Sheet and refresh to see updated data

## How Syncing Works

### Automatic Sync (When Online)
1. When you save a sale/inventory/credit entry, it's stored locally first
2. The entry is marked as "Pending" in the sync queue
3. Every 30 seconds, if you're online, SalesSpeak checks for pending records
4. Any pending records are uploaded to Google Sheets
5. Once uploaded, the record is marked as "Synced"

### Manual Sync
1. Click **Manual Sync** in the sidebar to force an immediate sync
2. Useful when coming back online or to verify data reached Google Sheets

### Offline Behavior
- When offline, all entries save to local SQLite database
- No errors shown (app knows you're offline)
- Once online, automatic sync catches up
- No data is lost

## Common Issues & Solutions

### Issue: "Authentication token not found" Error
**Solution:**
- Make sure the JSON file is placed correctly (step Phase 3)
- Check that the file name is exactly `google_service_account.json`
- Restart the app after placing the file
- Check browser console for detailed error message

### Issue: "Permission denied" or "Sheet not shared"
**Solution:**
- Copy the service account email from your JSON file
- Open the Google Sheet
- Click **Share** and re-add the service account email with **Editor** permission

### Issue: Data not appearing in Google Sheet
**Solution:**
- Click **Manual Sync** in the sidebar
- Wait 5 seconds and refresh the Google Sheet
- Check the **sync_log** tab in Google Sheet for errors

### Issue: "AttributeError: 'NoneType' object has no attribute 'open'"
**Solution:**
- The Google Sheets client failed to initialize
- Check that the JSON file exists and is valid
- Try deleting the JSON file and re-downloading it from Google Cloud Console
- Verify the service account has proper permissions

## How to Use Data in Google Sheets for Analysis

Once synced, your Google Sheet contains structured data you can analyze:

### Sales Analysis
- **Total Revenue**: Sum of `selling_price × quantity` from sales sheet
- **Total Profit**: Sum of the `profit` column from sales sheet
- **Sales by Category**: Use QUERY or pivot table to group by category
- **Daily/Weekly/Monthly Trends**: Create charts using date column

### Inventory Analysis
- **Stock Value**: Sum of `current_stock × cost_price`
- **Inventory Turnover**: Compare stock changes over time
- **Low Stock Alerts**: Filter items where `current_stock < reorder_level`
- **Out of Stock**: Filter items where `current_stock ≤ 0`

### Credit Analysis
- **Outstanding Credit**: Sum where `status = "Pending"`
- **Paid Credit**: Sum where `status = "Paid"`
- **Days Outstanding**: Compare today's date with `due_date`

### Example: Create a Pivot Table
1. Open your Google Sheet
2. Select the **sales** tab
3. Click **Data** → **Pivot Table**
4. Create rows for `category`, columns for `payment_method`, values as SUM of `profit`
5. This shows profit by category and payment method

## Security & Best Practices

1. **Keep JSON File Private**
   - Never commit it to GitHub or share it publicly
   - Add `google_service_account.json` to `.gitignore`

2. **Regenerate Key if Compromised**
   - If you accidentally share the JSON file:
   - Go to Google Cloud Console → Service Account → KEYS
   - Click the delete icon (trash) on the compromised key
   - Create a new key

3. **Backup Your Local Database**
   - Your local SQLite database is in `sales_data.db`
   - Back it up regularly (copy to a safe location)
   - Google Sheets is a backup, not a replacement

4. **Verify Sync is Working**
   - Weekly, check Google Sheet to ensure data is syncing
   - Look at `sync_log` tab for any failed syncs

## Next Steps

1. ✅ Complete Phase 1-3 setup above
2. ✅ Test with sample data (Phase 4)
3. ✅ Monitor sync status in sidebar
4. ✅ Use Google Sheet for analysis and reporting
5. ✅ Share Google Sheet with accountant/manager for review

## Support

If you encounter issues:
1. Check the **sync_log** tab in Google Sheet for error messages
2. Look at the browser console (F12) for detailed Python error tracebacks
3. Check that service account email is added to the Google Sheet

---

**SalesSpeak Version**: 1.0
**Last Updated**: 2025

# Sales & Inventory Management System

## Overview
A comprehensive sales and inventory management application built with Streamlit and Google Sheets integration. This system helps small businesses track sales, manage inventory, handle customer credits, and analyze business performance with real-time data synchronization.

**Last Updated:** November 8, 2025

## Purpose
Enable store owners to quickly record sales transactions using voice or manual input, track inventory levels, manage customer credit sales, and gain insights through analytics - all while syncing data to Google Sheets for remote access.

## Current Features

### Core Functionality
- **Sales Entry**: Record sales with voice or manual input
- **Inventory Management**: Auto-updating stock levels with low-stock alerts
- **Customer Credit Ledger**: Track credit sales with payment status
- **Analytics Dashboard**: Daily/monthly sales insights with charts
- **Reports**: Generate printable daily sales reports
- **Google Sheets Integration**: Real-time data sync for remote access

### Page Structure
1. **Dashboard** - Overview with key metrics, sales trends, top items
2. **Sales Entry** - Voice and manual input for recording sales
3. **Credit Ledger** - Manage customer credit sales and payments
4. **Inventory** - View stock levels, filter by category, low-stock alerts
5. **Analytics** - Sales trends, profit analysis, product performance
6. **Reports** - Generate daily sales reports for printing

## Project Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Data Storage**: Google Sheets (via gspread)
- **Speech Recognition**: SpeechRecognition + streamlit-audiorecorder
- **Visualizations**: Plotly
- **Data Processing**: Pandas, NumPy

### Key Files
- `app.py` - Main Streamlit application with all page logic
- `sheets_manager.py` - Google Sheets integration and data management
- `.streamlit/config.toml` - Streamlit server configuration

### Google Sheets Structure
The application creates a spreadsheet with 4 worksheets:
1. **Sales** - Date, Time, Item, Category, Quantity, Cost/Selling Price, Profit, Payment Method
2. **Inventory** - Item Name, Category, Stock, Prices, Reorder Level
3. **Credit** - Date, Customer Name, Phone, Amount, Due Date, Status
4. **Purchases** - Date, Item, Category, Quantity, Cost, Supplier

## Recent Changes

### November 8, 2025
- ✅ Initial application development completed
- ✅ Implemented custom `ReplitCredentials` class for Google Sheets authentication
- ✅ Added automatic token refresh with 50-minute expiry
- ✅ Fixed profit variable initialization bug for zero-cost items
- ✅ Installed ffmpeg for audio processing
- ✅ Set up multi-page navigation with 6 sections
- ✅ Created comprehensive dashboard with charts and metrics
- ✅ Implemented speech-to-text for faster data entry

## User Preferences
- **Language**: English
- **Currency**: Indian Rupees (₹)
- **Categories**: Groceries, Vegetables, Fruits, Dairy, Snacks, Beverages, Others
- **Payment Methods**: Cash, UPI, Card, Credit

## How It Works

### Sales Entry Flow
1. User opens Sales Entry page
2. Option 1: Click microphone and speak sale details
3. Option 2: Manually fill in item name, category, quantity, prices
4. System calculates profit/margin automatically
5. Click "Save Sale" to store in Google Sheets
6. Inventory automatically updates with reduced stock

### Credit Management Flow
1. Navigate to Credit Ledger
2. Add new credit sale with customer details
3. View all credits with status filter
4. Update payment status when customer pays

### Inventory Tracking
- Stock levels update automatically when sales are recorded
- Low stock alerts appear when Current Stock < Reorder Level
- View by category or stock status
- Category-wise stock value visualization

## Authentication
- Uses Replit Google Sheets connector
- Automatic token refresh every 50 minutes
- No manual credential management required

## Future Enhancements (Planned)
- [ ] Expiry date tracking with alerts
- [ ] Reorder point suggestions based on sales velocity
- [ ] Slow-moving stock reports
- [ ] Sales forecasting with time series analysis
- [ ] OCR receipt upload for automatic data entry
- [ ] Purchase order management
- [ ] Basic login authentication for multi-user access
- [ ] Payment reminder notifications for overdue credits
- [ ] Weekly and monthly detailed analytics reports
- [ ] Price optimization recommendations

## Known Limitations
- Speech recognition requires good audio quality
- Google Sheets API has rate limits (100 requests/100 seconds)
- Token refresh requires active internet connection
- Voice parsing is basic (may not handle complex phrases)

## Troubleshooting

### If Google Sheets is not updating:
1. Check that the Google Sheets connector is authorized
2. Verify the spreadsheet "Sales Management System" exists
3. Check workflow logs for authentication errors

### If voice entry fails:
1. Ensure microphone permissions are granted
2. Speak clearly with pauses between item details
3. Use manual entry as fallback

### If data doesn't appear:
1. Refresh the page
2. Check the Google Sheets spreadsheet directly
3. Verify internet connection

## Development Notes
- The app uses Streamlit's session state for page navigation
- Google Sheets operations are cached in SheetsManager
- All timestamps use local server time
- Profit calculations handle zero-cost scenarios gracefully

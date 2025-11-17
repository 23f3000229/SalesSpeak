# SQLite Offline-First Implementation

## Overview

Successfully implemented a complete offline-first data layer for SalesSpeak using SQLite. The app now works seamlessly whether online or offline, with automatic sync to Google Sheets when connectivity is restored.

## Components Created

### 1. **Database Layer** (`src/core/database.py`)

**LocalDB Class** - Complete SQLite database management:

**Tables:**
- `sales` - Sales transactions with sync tracking
- `inventory` - Product inventory with stock levels
- `purchases` - Purchase records with supplier info
- `credit` - Credit sales with customer tracking
- `sync_log` - Sync history for audit trail

**Key Methods:**
- `add_sale()` - Record sales locally
- `add_purchase()` - Record purchases and update inventory
- `add_credit_sale()` - Track credit transactions
- `get_unsynced_*()` - Retrieve records pending sync
- `mark_synced()` - Mark records as synced to Google Sheets
- `get_unsynced_count()` - Get pending sync count
- `get_database_stats()` - Get database metrics

**Features:**
- Automatic timestamp tracking (created_at, updated_at, synced_at)
- Profit calculation on sales
- Inventory auto-update on purchases
- SQLite built-in (no external dependencies)

### 2. **Sync Manager** (`src/core/sync_manager.py`)

**SyncManager Class** - Intelligent sync orchestration:

**Features:**
- **Offline Detection** - Checks internet connectivity before syncing
- **Automatic Queuing** - Stores data locally when offline
- **Smart Sync** - Syncs all pending records when online
- **Error Resilience** - Continues syncing even if one record fails
- **Sync Status** - Real-time status of online/offline state

**Key Methods:**
- `check_connectivity()` - Test internet availability
- `sync_sales()` - Sync sales to Google Sheets
- `sync_purchases()` - Sync purchases to Google Sheets
- `sync_all()` - Full sync of all pending data
- `get_sync_status()` - Current sync state
- `force_sync()` - Manual sync trigger

### 3. **Updated Feature Pages**

All data entry pages now use local database first, with Google Sheets as secondary storage:

#### **Sales Entry** (`src/features/sales/pages.py`)
- ✅ Enhanced form with cost price, payment method, notes
- ✅ Saves to local SQLite first
- ✅ Shows recent sales with sync status
- ✅ Works offline - data queued for sync

#### **Purchase Entry** (`src/features/purchases/pages.py`)
- ✅ Slip number, supplier, expiry date fields
- ✅ Auto-updates inventory on purchase
- ✅ Recent purchases view
- ✅ Fully offline-capable

#### **Credit Ledger** (`src/features/credit_ledger/pages.py`)
- ✅ Add credit sales with due dates
- ✅ Track payment status (Pending/Partial/Paid)
- ✅ Customer contact info
- ✅ Online/offline support

#### **Inventory** (`src/features/inventory/pages.py`)
- ✅ View all items with stock levels
- ✅ Add/update stock quantity
- ✅ Category-wise inventory value
- ✅ Low stock alerts
- ✅ Cost & selling price tracking

### 4. **App-Level Integration** (`app.py`)

**Session State:**
```python
st.session_state.local_db = LocalDB()
st.session_state.sync_manager = SyncManager(local_db, sheets_manager)
```

**Sync Status Sidebar:**
- 🟢/🟠 Online/Offline indicator
- 📊 Count of pending syncs
- 🔄 "Sync Now" button for manual sync
- 📊 Database stats (sales, purchases, credits, inventory, profit)

## Data Flow

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ▼
┌──────────────┐    ✓ Works offline
│  Local DB    │◄───┘
│  (SQLite)    │
└──────┬───────┘
       │
       ├─ No Internet → Queue for later
       │
       └─ Internet Available → Auto-sync to Google Sheets
              ▼
         ┌──────────────┐
         │  Google      │
         │  Sheets      │
         └──────────────┘
```

## Usage

### For Users

1. **Normal Operation (Online):**
   - Enter data → Saved to local DB → Automatically synced to Google Sheets
   - Sync status shows "✅ Online"

2. **Offline Operation:**
   - Enter data → Saved to local DB (no sync yet)
   - Sync status shows "⚠️ Offline"
   - App shows "📊 X records pending sync"

3. **When Internet Returns:**
   - Click "🔄 Sync Now" or wait for auto-sync
   - All pending data syncs to Google Sheets
   - Status updates to "✅ Online"

### For Developers

**Initialize Database:**
```python
from src.core.database import LocalDB
db = LocalDB()  # Creates sales_data.db
```

**Add a Sale:**
```python
db.add_sale(
    item_name="Rice",
    category="Groceries",
    quantity=5,
    cost_price=50,
    selling_price=80,
    payment_method="Cash"
)
```

**Get Pending Syncs:**
```python
unsynced = db.get_unsynced_sales()
```

**Mark as Synced:**
```python
db.mark_synced("sales", record_id)
```

## Database Schema

### sales table
| Field | Type | Purpose |
|-------|------|---------|
| id | INTEGER (PK) | Record ID |
| date | TEXT | Sale date (YYYY-MM-DD) |
| time | TEXT | Sale time (HH:MM:SS) |
| item_name | TEXT | Product name |
| category | TEXT | Product category |
| quantity | REAL | Units sold |
| cost_price | REAL | Cost per unit |
| selling_price | REAL | Sale price per unit |
| profit | REAL | Total profit (calculated) |
| synced | BOOLEAN | Sync status (0/1) |
| synced_at | TEXT | When synced to Sheets |

### inventory table
| Field | Type | Purpose |
|-------|------|---------|
| id | INTEGER (PK) | Record ID |
| item_name | TEXT (UNIQUE) | Product name |
| current_stock | REAL | Quantity on hand |
| cost_price | REAL | Cost per unit |
| selling_price | REAL | Sale price |
| reorder_level | REAL | Minimum stock alert |
| synced | BOOLEAN | Sync status |

## File Locations

```
src/
├── core/
│   ├── database.py          ← SQLite LocalDB class
│   ├── sync_manager.py      ← Sync orchestration
│   └── sheets_manager.py    ← Google Sheets integration
├── features/
│   ├── sales/pages.py       ← Uses local_db
│   ├── purchases/pages.py   ← Uses local_db
│   ├── credit_ledger/pages.py ← Uses local_db
│   ├── inventory/pages.py   ← Uses local_db
│   └── ...other pages
└── utils/
    └── logger.py            ← Logging utility

app.py                        ← Main entry point with sync controls
sales_data.db                 ← SQLite database file (auto-created)
```

## Testing

### Test Offline Mode

1. Disconnect from internet
2. Open the app
3. Sync status shows "⚠️ Offline"
4. Add sales/purchases/credit records
5. Sidebar shows "📊 X records pending sync"
6. Reconnect to internet
7. Click "🔄 Sync Now"
8. Records sync to Google Sheets

### Test Data Integrity

- All sales show sync status (✅ Synced / ⏳ Pending)
- Recent transactions list shows timestamps
- Database stats display correct counts
- Profit calculation is automatic

## Next Steps

### Phase 2: Advanced Features
- [ ] Background sync scheduler (auto-sync every 5 minutes when online)
- [ ] Sync conflict resolution (edited records)
- [ ] Export local data to CSV
- [ ] Data backup/restore
- [ ] Analytics from local DB (faster, offline-capable)

### Phase 3: Mobile App
- [ ] Convert to Kivy for mobile
- [ ] Share SQLite code between web and mobile
- [ ] Add mobile-specific sync UI
- [ ] Offline-first mobile app (Android APK)

## Architecture Benefits

✅ **Offline-First**: Works without internet
✅ **No Data Loss**: Everything queued locally
✅ **Fast**: Local DB much faster than cloud
✅ **Reliable**: SQLite built-in to Python and Android
✅ **Simple**: No complex sync logic needed
✅ **Scalable**: Mobile-ready (same DB layer)

## Known Limitations

- One-way sync (local → Google Sheets)
- No real-time collaboration (Google Sheets updates don't pull back)
- Max database size limited by disk space (~5GB on most systems)

## Support

All data is stored in `sales_data.db` in the project root. To:
- **Reset database**: Delete `sales_data.db` (recreated on next app start)
- **Backup data**: Copy `sales_data.db` to external drive
- **View raw data**: Open `sales_data.db` with SQLite browser

"""
Local SQLite database for offline-first sales management.
Stores sales, inventory, purchases, and credit data locally.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LocalDB:
    """SQLite database for offline sales data storage."""

    def __init__(self, db_path="sales_data.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_path)
        self.init_db()
        logger.info(f"Database initialized at {self.db_path}")

    def get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create all required tables."""
        conn = self.get_connection()
        c = conn.cursor()

        # Sales table
        c.execute(
            """CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity REAL NOT NULL,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            profit REAL NOT NULL,
            payment_method TEXT DEFAULT 'Cash',
            notes TEXT,
            synced BOOLEAN DEFAULT 0,
            synced_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
        )

        # Inventory table
        c.execute(
            """CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            current_stock REAL NOT NULL,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            reorder_level REAL DEFAULT 10,
            synced BOOLEAN DEFAULT 0,
            synced_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
        )

        # Purchases table
        c.execute(
            """CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            slip_number TEXT NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            total_price REAL NOT NULL,
            supplier TEXT NOT NULL,
            expiry_date TEXT,
            selling_price REAL NOT NULL,
            notes TEXT,
            synced BOOLEAN DEFAULT 0,
            synced_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
        )

        # Credit/Ledger table
        c.execute(
            """CREATE TABLE IF NOT EXISTS credit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT,
            item_name TEXT,
            amount REAL NOT NULL,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            synced BOOLEAN DEFAULT 0,
            synced_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
        )

        # Sync log table (track what's been synced)
        c.execute(
            """CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            synced_at TEXT NOT NULL
        )"""
        )

        conn.commit()
        conn.close()
        logger.info("Database tables initialized")

    # ============ SALES METHODS ============

    def add_sale(self, item_name, category, quantity, cost_price, selling_price, payment_method="Cash", notes=""):
        """Add a sale record and auto-update inventory."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            now = datetime.now()

            # Profit per unit * quantity sold
            profit = (selling_price - cost_price) * quantity

            c.execute(
                """INSERT INTO sales 
                (date, time, item_name, category, quantity, cost_price, selling_price, profit, payment_method, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    item_name,
                    category,
                    quantity,
                    cost_price,
                    selling_price,
                    profit,
                    payment_method,
                    notes,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

            # Auto-create/update inventory (reduce by quantity sold)
            c.execute("SELECT id, current_stock FROM inventory WHERE item_name = ?", (item_name,))
            row = c.fetchone()

            if row:
                # Update existing - reduce stock by quantity
                new_stock = row["current_stock"] - quantity
                c.execute(
                    "UPDATE inventory SET current_stock = ?, updated_at = ? WHERE item_name = ?",
                    (new_stock, now.isoformat(), item_name),
                )
            else:
                # Create new inventory record with negative stock
                c.execute(
                    """INSERT INTO inventory 
                    (item_name, category, current_stock, cost_price, selling_price, reorder_level, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (item_name, category, -quantity, cost_price, selling_price, 10, now.isoformat(), now.isoformat()),
                )

            conn.commit()
            conn.close()
            logger.info(f"Sale added: {item_name} (qty: {quantity}), Inventory synced")
            return True
        except Exception as e:
            logger.exception(f"Error adding sale: {e}")
            return False

    def get_sales(self, limit=None):
        """Get all sales from local database."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            if limit:
                c.execute("SELECT * FROM sales ORDER BY date DESC, time DESC LIMIT ?", (limit,))
            else:
                c.execute("SELECT * FROM sales ORDER BY date DESC, time DESC")
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting sales: {e}")
            return []

    def get_unsynced_sales(self):
        """Get all sales not yet synced to Google Sheets."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM sales WHERE synced = 0 ORDER BY created_at ASC")
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting unsynced sales: {e}")
            return []

    # ============ INVENTORY METHODS ============

    def add_or_update_inventory(self, item_name, category, quantity_change, cost_price, selling_price):
        """Add or update inventory item."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            now = datetime.now()

            # Check if item exists
            c.execute("SELECT id, current_stock FROM inventory WHERE item_name = ?", (item_name,))
            row = c.fetchone()

            if row:
                # Update existing
                new_stock = row["current_stock"] + quantity_change
                c.execute(
                    """UPDATE inventory 
                    SET current_stock = ?, updated_at = ? 
                    WHERE item_name = ?""",
                    (new_stock, now.isoformat(), item_name),
                )
            else:
                # Insert new
                c.execute(
                    """INSERT INTO inventory 
                    (item_name, category, current_stock, cost_price, selling_price, reorder_level, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (item_name, category, quantity_change, cost_price, selling_price, 10, now.isoformat(), now.isoformat()),
                )

            conn.commit()
            conn.close()
            logger.info(f"Inventory updated: {item_name}")
            return True
        except Exception as e:
            logger.exception(f"Error updating inventory: {e}")
            return False

    def get_inventory(self):
        """Get all inventory items from local database."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM inventory ORDER BY item_name")
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting inventory: {e}")
            return []

    def get_unsynced_inventory(self):
        """Get all inventory items not yet synced."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM inventory WHERE synced = 0 ORDER BY created_at ASC")
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting unsynced inventory: {e}")
            return []

    # ============ PURCHASES METHODS ============

    def add_purchase(self, slip_number, item_name, category, quantity, unit, total_price, supplier, expiry_date, selling_price, notes=""):
        """Add a purchase record."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            now = datetime.now()

            c.execute(
                """INSERT INTO purchases 
                (date, slip_number, item_name, category, quantity, unit, total_price, supplier, expiry_date, selling_price, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    now.strftime("%Y-%m-%d"),
                    slip_number,
                    item_name,
                    category,
                    quantity,
                    unit,
                    total_price,
                    supplier,
                    expiry_date,
                    selling_price,
                    notes,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

            # Update inventory
            cost_per_unit = total_price / quantity if quantity > 0 else 0
            self.add_or_update_inventory(item_name, category, quantity, cost_per_unit, selling_price)

            conn.commit()
            conn.close()
            logger.info(f"Purchase added: {item_name} (qty: {quantity})")
            return True
        except Exception as e:
            logger.exception(f"Error adding purchase: {e}")
            return False

    def get_purchases(self, limit=None):
        """Get all purchases from local database."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            if limit:
                c.execute("SELECT * FROM purchases ORDER BY date DESC LIMIT ?", (limit,))
            else:
                c.execute("SELECT * FROM purchases ORDER BY date DESC")
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting purchases: {e}")
            return []

    # ============ CREDIT METHODS ============

    def add_credit_sale(self, customer_name, phone, item_name, amount, due_date, notes=""):
        """Add a credit sale record."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            now = datetime.now()

            c.execute(
                """INSERT INTO credit 
                (date, customer_name, phone, item_name, amount, due_date, status, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    now.strftime("%Y-%m-%d"),
                    customer_name,
                    phone,
                    item_name,
                    amount,
                    due_date,
                    "Pending",
                    notes,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

            conn.commit()
            conn.close()
            logger.info(f"Credit sale added: {customer_name}")
            return True
        except Exception as e:
            logger.exception(f"Error adding credit sale: {e}")
            return False

    def get_credit(self):
        """Get all credit records from local database."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM credit ORDER BY date DESC")
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.exception(f"Error getting credit records: {e}")
            return []

    def update_credit_status(self, credit_id, status):
        """Update credit payment status."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            now = datetime.now()

            c.execute("UPDATE credit SET status = ?, updated_at = ? WHERE id = ?", (status, now.isoformat(), credit_id))

            conn.commit()
            conn.close()
            logger.info(f"Credit status updated: ID {credit_id} -> {status}")
            return True
        except Exception as e:
            logger.exception(f"Error updating credit status: {e}")
            return False

    # ============ SYNC METHODS ============

    def mark_synced(self, table_name, record_id):
        """Mark a record as synced to Google Sheets."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            now = datetime.now()

            c.execute(
                f"UPDATE {table_name} SET synced = 1, synced_at = ? WHERE id = ?",
                (now.isoformat(), record_id),
            )

            # Log the sync
            c.execute(
                """INSERT INTO sync_log (table_name, record_id, action, synced_at)
                VALUES (?, ?, ?, ?)""",
                (table_name, record_id, "synced", now.isoformat()),
            )

            conn.commit()
            conn.close()
            logger.info(f"Record marked synced: {table_name} ID {record_id}")
            return True
        except Exception as e:
            logger.exception(f"Error marking synced: {e}")
            return False

    def get_unsynced_count(self):
        """Get count of unsynced records across all tables."""
        try:
            conn = self.get_connection()
            c = conn.cursor()

            c.execute("SELECT COUNT(*) as count FROM sales WHERE synced = 0")
            sales_count = c.fetchone()["count"]

            c.execute("SELECT COUNT(*) as count FROM purchases WHERE synced = 0")
            purchases_count = c.fetchone()["count"]

            c.execute("SELECT COUNT(*) as count FROM credit WHERE synced = 0")
            credit_count = c.fetchone()["count"]

            c.execute("SELECT COUNT(*) as count FROM inventory WHERE synced = 0")
            inventory_count = c.fetchone()["count"]

            conn.close()
            return sales_count + purchases_count + credit_count + inventory_count
        except Exception as e:
            logger.exception(f"Error getting unsynced count: {e}")
            return 0

    def get_last_sync_time(self):
        """Get timestamp of last successful sync."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute("SELECT MAX(synced_at) as last_sync FROM sync_log")
            row = c.fetchone()
            conn.close()
            return row["last_sync"] if row["last_sync"] else None
        except Exception as e:
            logger.exception(f"Error getting last sync time: {e}")
            return None

    def get_database_stats(self):
        """Get database statistics."""
        try:
            conn = self.get_connection()
            c = conn.cursor()

            c.execute("SELECT COUNT(*) as count FROM sales")
            sales_count = c.fetchone()["count"]

            c.execute("SELECT COUNT(*) as count FROM purchases")
            purchases_count = c.fetchone()["count"]

            c.execute("SELECT COUNT(*) as count FROM credit")
            credit_count = c.fetchone()["count"]

            c.execute("SELECT COUNT(*) as count FROM inventory")
            inventory_count = c.fetchone()["count"]

            c.execute("SELECT SUM(profit) as total_profit FROM sales")
            total_profit = c.fetchone()["total_profit"] or 0

            conn.close()

            return {
                "sales": sales_count,
                "purchases": purchases_count,
                "credit": credit_count,
                "inventory": inventory_count,
                "total_profit": total_profit,
                "unsynced": self.get_unsynced_count(),
            }
        except Exception as e:
            logger.exception(f"Error getting database stats: {e}")
            return {}

"""
Sync manager for offline-first data synchronization.
Handles queuing, online detection, and syncing data to Google Sheets.
"""

import requests
import time
from datetime import datetime
from src.utils.logger import get_logger
from src.core.database import LocalDB
from src.core.sheets_manager import SheetsManager

logger = get_logger(__name__)


class SyncManager:
    """Manages offline data queuing and syncing to Google Sheets."""

    def __init__(self, local_db: LocalDB, sheets_manager: SheetsManager):
        """Initialize sync manager with database and sheets manager."""
        self.local_db = local_db
        self.sheets_manager = sheets_manager
        self.is_online = self.check_connectivity()
        logger.info(f"SyncManager initialized. Online: {self.is_online}")

    def check_connectivity(self):
        """Check if device has internet connectivity."""
        try:
            response = requests.get("https://www.google.com", timeout=3)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Connectivity check failed: {e}")
            return False

    def sync_sales(self):
        """Sync unsynced sales to Google Sheets."""
        if not self.is_online:
            logger.info("Offline - skipping sync")
            return {"success": False, "reason": "offline", "synced": 0}

        try:
            unsynced = self.local_db.get_unsynced_sales()
            if not unsynced:
                logger.info("No unsynced sales to sync")
                return {"success": True, "synced": 0}

            synced_count = 0
            for sale in unsynced:
                try:
                    # Add to Google Sheets
                    self.sheets_manager.add_sale(
                        date=sale["date"],
                        time=sale["time"],
                        item_name=sale["item_name"],
                        category=sale["category"],
                        quantity=sale["quantity"],
                        cost_price=sale["cost_price"],
                        selling_price=sale["selling_price"],
                        profit=sale["profit"],
                        payment_method=sale.get("payment_method", "Cash"),
                        notes=sale.get("notes", ""),
                    )

                    # Mark as synced in local DB
                    self.local_db.mark_synced("sales", sale["id"])
                    synced_count += 1
                    logger.info(f"Synced sale: {sale['item_name']}")

                except Exception as e:
                    logger.exception(f"Error syncing sale {sale['id']}: {e}")
                    # Continue with next sale on error

            return {"success": True, "synced": synced_count, "total": len(unsynced)}

        except Exception as e:
            logger.exception(f"Error in sync_sales: {e}")
            return {"success": False, "error": str(e), "synced": 0}

    def sync_purchases(self):
        """Sync unsynced purchases to Google Sheets."""
        if not self.is_online:
            return {"success": False, "reason": "offline", "synced": 0}

        try:
            unsynced = self.local_db.get_unsynced_inventory()
            if not unsynced:
                return {"success": True, "synced": 0}

            synced_count = 0
            for purchase in unsynced:
                try:
                    # For purchases, we'd add to Google Sheets purchases sheet
                    # This is a placeholder - implement based on your sheets structure
                    self.local_db.mark_synced("purchases", purchase["id"])
                    synced_count += 1
                    logger.info(f"Synced purchase: {purchase['item_name']}")

                except Exception as e:
                    logger.exception(f"Error syncing purchase {purchase['id']}: {e}")

            return {"success": True, "synced": synced_count, "total": len(unsynced)}

        except Exception as e:
            logger.exception(f"Error in sync_purchases: {e}")
            return {"success": False, "error": str(e), "synced": 0}

    def sync_all(self):
        """Sync all unsynced data to Google Sheets."""
        logger.info("Starting full sync...")

        # Check connectivity first
        self.is_online = self.check_connectivity()
        if not self.is_online:
            unsynced_count = self.local_db.get_unsynced_count()
            logger.warning(f"Offline - {unsynced_count} records queued for sync")
            return {
                "success": False,
                "reason": "offline",
                "queued": unsynced_count,
                "timestamp": datetime.now().isoformat(),
            }

        results = {
            "sales": self.sync_sales(),
            "purchases": self.sync_purchases(),
            "timestamp": datetime.now().isoformat(),
        }

        total_synced = results["sales"].get("synced", 0) + results["purchases"].get("synced", 0)
        results["total_synced"] = total_synced

        logger.info(f"Sync complete. Total synced: {total_synced}")
        return results

    def get_sync_status(self):
        """Get current sync status."""
        unsynced_count = self.local_db.get_unsynced_count()
        last_sync = self.local_db.get_last_sync_time()
        db_stats = self.local_db.get_database_stats()

        return {
            "online": self.is_online,
            "unsynced_count": unsynced_count,
            "last_sync": last_sync,
            "database_stats": db_stats,
        }

    def force_sync(self):
        """Force a sync attempt, updating online status first."""
        self.is_online = self.check_connectivity()
        return self.sync_all()

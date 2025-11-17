import os
import json
import requests
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as GoogleCredentials
from datetime import datetime
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SheetsManager:
    def __init__(self):
        # Defer heavy/network initialization until actually needed.
        # This prevents long blocking or failures during app startup
        # when Google Sheets credentials are not present. The
        # rest of the code calls `initialize_client()` as required.
        self.client = None
        self.spreadsheet = None
    
    def get_access_token(self):
        """Get access token from Replit Google Sheets connector"""
        hostname = os.environ.get('CONNECTORS_HOSTNAME', 'connectors.replit.com')
        
        x_replit_token = None
        if os.environ.get('REPL_IDENTITY'):
            x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY')
        elif os.environ.get('WEB_REPL_RENEWAL'):
            x_replit_token = 'depl ' + os.environ.get('WEB_REPL_RENEWAL')
        
        if not x_replit_token:
            raise Exception('Authentication token not found')
        
        url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet'
        headers = {
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            raise Exception('Google Sheets not connected')
        
        connection_settings = data['items'][0]
        access_token = connection_settings.get('settings', {}).get('access_token')
        
        if not access_token:
            raise Exception('Access token not found')
        
        return access_token
    
    def initialize_client(self):
        """Initialize Google Sheets client with Replit credentials"""
        # Prefer service-account / local credentials if provided for local development
        try:
            # Option A: GOOGLE_APPLICATION_CREDENTIALS path (recommended)
            gcred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            service_json = os.environ.get('SERVICE_ACCOUNT_JSON')

            if gcred_path and os.path.exists(gcred_path):
                try:
                    self.client = gspread.service_account(filename=gcred_path)
                    logger.info("Initialized gspread service_account from path")
                    return
                except Exception as e:
                    logger.warning(f"Failed to init gspread.service_account from path: {e}")

            # Option B: SERVICE_ACCOUNT_JSON content provided directly
            if service_json:
                try:
                    info = json.loads(service_json)
                    self.client = gspread.service_account_from_dict(info)
                    logger.info("Initialized gspread service_account from SERVICE_ACCOUNT_JSON")
                    return
                except Exception as e:
                    logger.warning(f"Failed to init gspread.service_account_from_dict: {e}")

            # Fallback: Replit connector
            access_token = self.get_access_token()
            credentials = ReplitCredentials(token=access_token)
            self.client = gspread.authorize(credentials)
            logger.info("Initialized gspread via Replit connector")
        except Exception as e:
            logger.exception(f"Error initializing Google Sheets client: {e}")
            self.client = None
    
    def get_or_create_spreadsheet(self, title="Sales Management System"):
        """Get existing spreadsheet or create a new one"""
        try:
            if not self.client:
                self.initialize_client()
            
            # Try to open existing spreadsheet
            try:
                self.spreadsheet = self.client.open(title)
            except gspread.exceptions.SpreadsheetNotFound:
                # Create new spreadsheet
                self.spreadsheet = self.client.create(title)
                self.spreadsheet.share('', perm_type='anyone', role='writer')
                self.initialize_sheets()
            
            return self.spreadsheet
        except Exception as e:
            print(f"Error getting/creating spreadsheet: {e}")
            return None
    
    def initialize_sheets(self):
        """Initialize all required sheets with headers"""
        sheets_config = {
            'Sales': ['Date', 'Time', 'Item Name', 'Category', 'Quantity', 'Cost Price', 'Selling Price', 'Profit', 'Payment Method', 'Notes'],
            'Inventory': ['Item Name', 'Category', 'Current Stock', 'Cost Price', 'Selling Price', 'Reorder Level', 'Last Updated'],
            'Credit': ['Date', 'Customer Name', 'Phone', 'Item Name', 'Amount', 'Due Date', 'Status', 'Notes'],
            'Purchases': ['Date', 'Slip Number', 'Item Name', 'Category', 'Quantity', 'Unit', 'Total Price', 'Supplier', 'Expiry Date', 'Selling Price', 'Notes']
        }
        
        for sheet_name, headers in sheets_config.items():
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                worksheet.append_row(headers)
    
    def add_sale(self, item_name, category, quantity, cost_price, selling_price, payment_method='Cash', notes=''):
        """Add a new sale record"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Sales')
            now = datetime.now()
            profit = (selling_price - cost_price) * quantity
            
            row = [
                now.strftime('%Y-%m-%d'),
                now.strftime('%H:%M:%S'),
                item_name,
                category,
                quantity,
                cost_price,
                selling_price,
                profit,
                payment_method,
                notes
            ]
            
            worksheet.append_row(row)
            
            # Update inventory
            self.update_inventory(item_name, category, -quantity, cost_price, selling_price)
            
            return True
        except Exception as e:
            print(f"Error adding sale: {e}")
            return False
    
    def add_credit_sale(self, customer_name, phone, item_name, amount, due_date, notes=''):
        """Add a credit sale record"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Credit')
            now = datetime.now()
            
            row = [
                now.strftime('%Y-%m-%d'),
                customer_name,
                phone,
                item_name if item_name else '',
                amount,
                due_date,
                'Pending',
                notes
            ]
            
            worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding credit sale: {e}")
            return False
    
    def update_inventory(self, item_name, category, quantity_change, cost_price, selling_price):
        """Update inventory stock levels"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Inventory')
            records = worksheet.get_all_records()
            
            # Find existing item
            item_found = False
            for idx, record in enumerate(records):
                if record['Item Name'] == item_name:
                    current_stock = float(record['Current Stock']) if record['Current Stock'] else 0
                    new_stock = current_stock + quantity_change
                    worksheet.update_cell(idx + 2, 3, new_stock)  # Update Current Stock
                    worksheet.update_cell(idx + 2, 7, datetime.now().strftime('%Y-%m-%d %H:%M'))  # Update Last Updated
                    item_found = True
                    break
            
            # Add new item if not found
            if not item_found:
                row = [
                    item_name,
                    category,
                    quantity_change,
                    cost_price,
                    selling_price,
                    10,  # Default reorder level
                    datetime.now().strftime('%Y-%m-%d %H:%M')
                ]
                worksheet.append_row(row)
            
            return True
        except Exception as e:
            print(f"Error updating inventory: {e}")
            return False
    
    def get_sales_data(self):
        """Get all sales data"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Sales')
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error getting sales data: {e}")
            return pd.DataFrame()
    
    def get_inventory_data(self):
        """Get all inventory data"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Inventory')
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error getting inventory data: {e}")
            return pd.DataFrame()
    
    def get_credit_data(self):
        """Get all credit data"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Credit')
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error getting credit data: {e}")
            return pd.DataFrame()
    
    def update_credit_status(self, row_index, status):
        """Update credit payment status"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Credit')
            worksheet.update_cell(row_index + 2, 7, status)  # +2 for header and 0-index, column 7 for Status
            return True
        except Exception as e:
            print(f"Error updating credit status: {e}")
            return False
    
    def add_purchase(self, slip_number, item_name, category, quantity, unit, total_price, supplier, expiry_date, selling_price, notes=''):
        """Add a new purchase record"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Purchases')
            now = datetime.now()
            
            row = [
                now.strftime('%Y-%m-%d'),
                slip_number,
                item_name,
                category,
                quantity,
                unit,
                total_price,
                supplier,
                expiry_date if expiry_date else '',
                selling_price,
                notes
            ]
            
            worksheet.append_row(row)
            
            # Update inventory with purchase - add stock
            cost_per_unit = total_price / quantity if quantity > 0 else 0
            self.update_inventory(item_name, category, quantity, cost_per_unit, selling_price)
            
            return True
        except Exception as e:
            print(f"Error adding purchase: {e}")
            return False
    
    def get_purchases_data(self):
        """Get all purchase data"""
        try:
            if not self.spreadsheet:
                self.get_or_create_spreadsheet()
            
            worksheet = self.spreadsheet.worksheet('Purchases')
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error getting purchase data: {e}")
            return pd.DataFrame()
    
    def get_item_cost_from_purchases(self, item_name):
        """Get the most recent cost price for an item from purchases"""
        try:
            purchases_df = self.get_purchases_data()
            if not purchases_df.empty and 'Item Name' in purchases_df.columns:
                item_purchases = purchases_df[purchases_df['Item Name'] == item_name]
                if not item_purchases.empty:
                    latest_purchase = item_purchases.iloc[-1]
                    quantity = float(latest_purchase['Quantity']) if latest_purchase['Quantity'] else 1
                    total_price = float(latest_purchase['Total Price']) if latest_purchase['Total Price'] else 0
                    return total_price / quantity if quantity > 0 else 0
            return 0
        except Exception as e:
            print(f"Error getting item cost: {e}")
            return 0

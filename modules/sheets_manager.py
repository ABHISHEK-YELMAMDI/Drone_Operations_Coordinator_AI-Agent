import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, date
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class GoogleSheetsManager:
    """Manages two-way sync with Google Sheets"""

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        if not self.credentials_path:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS_PATH not set in .env")

        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]

        self.client = None
        self.sheets: Dict = {}
        self.sheet_ids = {
            'pilot_roster': os.getenv('GOOGLE_SHEETS_PILOT_ROSTER_ID'),
            'drone_fleet': os.getenv('GOOGLE_SHEETS_DRONE_FLEET_ID'),
            'missions': os.getenv('GOOGLE_SHEETS_MISSIONS_ID')
        }

        self.connect()
        self.load_all_sheets()

    def connect(self) -> None:
        """Establish connection to Google Sheets API"""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path,
                self.scope
            )
            self.client = gspread.authorize(creds)
            logger.info("✅ Successfully connected to Google Sheets API")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {e}")
            raise

    def load_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Load a specific sheet by name"""
        try:
            if sheet_name not in self.sheet_ids:
                logger.error(f"Sheet name {sheet_name} not configured")
                return pd.DataFrame()

            sheet_id = self.sheet_ids[sheet_name]
            if not sheet_id or sheet_id.startswith('your_'):
                logger.error(f"Sheet ID for {sheet_name} not properly configured")
                return pd.DataFrame()

            # Open spreadsheet
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1

            # Get all records
            records = worksheet.get_all_records()

            if not records:
                logger.warning(f"No data found in {sheet_name}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(records)

            # Store in cache
            self.sheets[sheet_name] = {
                'worksheet': worksheet,
                'dataframe': df,
                'last_sync': datetime.now(),
                'headers': worksheet.row_values(1)
            }

            logger.info(f"📥 Loaded {sheet_name}: {len(df)} records")
            return df

        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found for {sheet_name}. Check sheet ID.")
        except gspread.exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {sheet_name}: {e}")

        return pd.DataFrame()

    def load_all_sheets(self) -> None:
        """Load all configured sheets"""
        for sheet_name in ['pilot_roster', 'drone_fleet', 'missions']:
            self.load_sheet(sheet_name)

    def get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        """Get sheet data from cache or load fresh"""
        if sheet_name in self.sheets:
            return self.sheets[sheet_name]['dataframe'].copy()
        return self.load_sheet(sheet_name)

    def update_record(self, sheet_name: str, record_id: str,
                     updates: Dict[str, Any], id_column: str = None) -> bool:
        """Update a record in the sheet"""
        try:
            if sheet_name not in self.sheets:
                logger.error(f"Sheet {sheet_name} not loaded")
                return False

            worksheet = self.sheets[sheet_name]['worksheet']
            df = self.sheets[sheet_name]['dataframe']
            headers = self.sheets[sheet_name]['headers']

            # Determine ID column
            if id_column is None:
                id_column = self._guess_id_column(sheet_name)

            # Find the row
            if id_column not in df.columns:
                logger.error(f"ID column {id_column} not found in {sheet_name}")
                return False

            row_idx = df.index[df[id_column] == record_id].tolist()
            if not row_idx:
                logger.error(f"Record {record_id} not found in {sheet_name}")
                return False

            row_num = row_idx[0] + 2  # +1 for header, +1 for 1-indexed

            # Update each field
            for field, value in updates.items():
                if field in headers:
                    col_num = headers.index(field) + 1
                    worksheet.update_cell(row_num, col_num, str(value))

                    # Update local cache
                    df.at[row_idx[0], field] = value
                else:
                    logger.warning(f"Field {field} not found in sheet headers")

            self.sheets[sheet_name]['last_sync'] = datetime.now()
            logger.info(f"✅ Updated {sheet_name} record {record_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update record: {e}")
            return False

    def add_record(self, sheet_name: str, record: Dict[str, Any]) -> bool:
        """Add a new record to the sheet"""
        try:
            if sheet_name not in self.sheets:
                logger.error(f"Sheet {sheet_name} not loaded")
                return False

            worksheet = self.sheets[sheet_name]['worksheet']
            headers = self.sheets[sheet_name]['headers']

            # Prepare row values in correct order
            row_values = []
            for header in headers:
                row_values.append(str(record.get(header, '')))

            # Append row
            worksheet.append_row(row_values)

            # Reload sheet to update cache
            self.load_sheet(sheet_name)

            logger.info(f"✅ Added new record to {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to add record: {e}")
            return False

    def _guess_id_column(self, sheet_name: str) -> str:
        """Guess the ID column based on sheet name"""
        if sheet_name == 'pilot_roster':
            return 'pilot_id'
        elif sheet_name == 'drone_fleet':
            return 'drone_id'
        elif sheet_name == 'missions':
            return 'mission_id'
        return 'id'

    def refresh_all(self) -> None:
        """Refresh all sheets from Google"""
        logger.info("🔄 Refreshing all sheets...")
        for sheet_name in list(self.sheets.keys()):
            self.load_sheet(sheet_name)

    def get_status(self) -> Dict:
        """Get status of all sheets"""
        status = {}
        for sheet_name, data in self.sheets.items():
            status[sheet_name] = {
                'records': len(data['dataframe']),
                'last_sync': data['last_sync'].strftime('%Y-%m-%d %H:%M:%S'),
                'columns': list(data['dataframe'].columns)
            }
        return status

# Create singleton instance (only if credentials are available)
try:
    sheets_manager = GoogleSheetsManager()
except Exception as e:
    logger.warning(f"Google Sheets not configured: {e}")
    sheets_manager = None

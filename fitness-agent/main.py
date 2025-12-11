import functions_framework
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os

# Import from config.py instead of hardcoding
from config import SPREADSHEET_ID

@functions_framework.http
def generate_workout(request):
    try:
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        
        if not creds_json:
            return "Error: GOOGLE_CREDENTIALS not set", 500
        
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        title = spreadsheet.get('properties', {}).get('title', 'Unknown')
        
        test_range = "Sheet1!A1"
        body = {"values": [["Connection test - it works!"]]}
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=test_range,
            valueInputOption="RAW",
            body=body
        ).execute()
        
        return f"Success! Connected to: {title}. Check cell A1."
        
    except Exception as e:
        return f"Error: {str(e)}", 500


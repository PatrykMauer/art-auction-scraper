import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the credentials
creds = Credentials.from_service_account_file(
    '<path-to-service-account-credentials-file>',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# Set up the Google Sheets API client
service = build('sheets', 'v4', credentials=creds)

# Specify the spreadsheet ID and range
spreadsheet_id = '<your spreadsheet ID>'
sheet_range = '<your sheet range>'

# Load the data from the JSON file
with open('<your JSON file>', 'r') as f:
    data = json.load(f)

# Convert the data to a list of rows
rows = []
for item in data:
    rows.append([item['column1'], item['column2'], item['column3']])

# Create the update request
update_request = {
    'appendCells': {
        'rows': {
            'values': rows
        },
        'fields': '*'
    }
}

# Execute the update request
try:
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={'requests': [update_request]}
    ).execute()
    print(f'{response.get("totalUpdatedCells")} cells appended.')
except HttpError as error:
    print(f'An error occurred: {error}')

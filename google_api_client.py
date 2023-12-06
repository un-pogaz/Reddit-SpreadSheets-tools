import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def _raw_input(value):
    return 'RAW' if value else 'USER_ENTERED'

class SpreadSheets():
    def __init__(self, spreadsheets_service, spreadsheet_id: str):
        self._spreadsheets =  spreadsheets_service
        self.spreadsheets_id = spreadsheet_id
    
    def append(self, range: str, values: list[list[str|int|float]], raw_input=False, overwrite=False):
        self._spreadsheets.values().append(
            spreadsheetId=self.spreadsheets_id,
            range=range,
            insertDataOption='OVERWRITE' if overwrite else 'INSERT_ROWS',
            valueInputOption=_raw_input(raw_input),
            body={'values': values},
        ).execute()
    
    def get(self, range: str) -> list[list[str|int|float]]:
        return self._spreadsheets.values().get(
                spreadsheetId=self.spreadsheets_id,
                range=range
            ).execute().get("values", [])
    
    def update(self, range: str, values: list[list[str|int|float]], raw_input=False):
        self._spreadsheets.values().update(
            spreadsheetId=self.spreadsheets_id,
            range=range,
            valueInputOption=_raw_input(raw_input),
            body={'values': values},
        ).execute()
    
    def clear(self, range: str):
        self._spreadsheets.values().clear(
            spreadsheetId=self.spreadsheets_id,
            range=range,
        ).execute()
    
    def batchClear(self, ranges: list[str]):
        self._spreadsheets.values().batchClear(
            spreadsheetId=self.spreadsheets_id,
            body={'ranges': ranges},
        ).execute()


class GoogleApiClient():
    def __init__(self, credentials_oauth2: str, token_json: str, scopes: list[str]):
        self._creds = None
        
        print('Google Api Client: connecting...')
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_json):
            self._creds = Credentials.from_authorized_user_file(token_json, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_oauth2, scopes)
                self._creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_json, 'w') as token:
                token.write(self._creds.to_json())
        print('Google Api Client: connection completed')

class SpreadSheetsClient(GoogleApiClient):
    
    def __init__(self, credentials_oauth2: str, token_json: str, readonly: bool = False):
            scopes = []
            if readonly:
                scopes.append("https://www.googleapis.com/auth/spreadsheets.readonly")
            else:
                scopes.append("https://www.googleapis.com/auth/spreadsheets")
            
            super().__init__(credentials_oauth2, token_json, scopes)
            
            self._service = build("sheets", "v4", credentials=self._creds)
            self._spreadsheets = self._service.spreadsheets()
    
    def new_spread_sheets(self, spreadsheets_id: str) -> SpreadSheets:
        return SpreadSheets(self._spreadsheets, spreadsheets_id)

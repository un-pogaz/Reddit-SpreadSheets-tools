from typing import Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _raw_input(value):
    return 'RAW' if value else 'USER_ENTERED'

class SpreadSheets():
    def __init__(self, spreadsheets_service, spreadsheet_id: str):
        self._spreadsheets_service = spreadsheets_service
        self.spreadsheets_id = spreadsheet_id
    
    def getSpreadsheetsMetadata(self) -> dict[str, Any]:
        return self._spreadsheets_service.get(
                spreadsheetId=self.spreadsheets_id
            ).execute()
    
    def append(self, range: str, values: list[list[str|int|float]], raw_input=False, overwrite=False):
        self._spreadsheets_service.values().append(
            spreadsheetId=self.spreadsheets_id,
            range=range,
            insertDataOption='OVERWRITE' if overwrite else 'INSERT_ROWS',
            valueInputOption=_raw_input(raw_input),
            body={'values': values},
        ).execute()
    
    def get(self, range: str) -> list[list[str|int|float]]:
        return self._spreadsheets_service.values().get(
                spreadsheetId=self.spreadsheets_id,
                range=range
            ).execute().get("values", [])
    
    def update(self, range: str, values: list[list[str|int|float]], raw_input=False):
        self._spreadsheets_service.values().update(
            spreadsheetId=self.spreadsheets_id,
            range=range,
            valueInputOption=_raw_input(raw_input),
            body={'values': values},
        ).execute()
    
    def clear(self, range: str):
        self._spreadsheets_service.values().clear(
            spreadsheetId=self.spreadsheets_id,
            range=range,
        ).execute()
    
    def batchClear(self, ranges: list[str]):
        self._spreadsheets_service.values().batchClear(
            spreadsheetId=self.spreadsheets_id,
            body={'ranges': ranges},
        ).execute()
    
    def batchUpdateSpreadsheets(self, requests: list[dict[str, Any]]):
        self._spreadsheets_service.batchUpdate(
            spreadsheetId=self.spreadsheets_id,
            body={'requests': requests},
        ).execute()


class GoogleApiClient():
    def __init__(self,
            discovery_url: str = None,
            developer_api_key: str = None,
            credentials_oauth2: str = None,
            token_json: str = None,
            scopes: str = None,
        ):
        import os.path

        import httplib2
        
        self._creds = None
        self._service = None
        
        print('Google Api Client: connecting...')
        
        if developer_api_key:
            ## API keys
            
            # Using a Api key give access to read only public data
            self._service = build("sheets", "v4",
                                    http=httplib2.Http(),
                                    discoveryServiceUrl=discovery_url,
                                    developerKey=developer_api_key)
        
        if credentials_oauth2 and token_json:
            ## OAuth
            
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists(token_json):
                self._creds = Credentials.from_authorized_user_file(token_json, scopes)
            
            def run_local_server():
                flow = InstalledAppFlow.from_client_secrets_file(credentials_oauth2, scopes)
                self._creds = flow.run_local_server(port=0)
            
            # If there are no (valid) credentials available, let the user log in.
            if not self._creds or not self._creds.valid:
                try:
                    if self._creds and self._creds.expired and self._creds.refresh_token:
                        self._creds.refresh(Request())
                    else:
                        run_local_server()
                except:
                    run_local_server()
                # Save the credentials for the next run
                with open(token_json, 'w') as token:
                    token.write(self._creds.to_json())
            
            self._service = build("sheets", "v4", credentials=self._creds)
        
        if not self._service:
            raise ValueError('Google Service Client can be initialized because none of developer_api_key, credentials_oauth2 or token_json are provided.')
        
        print('Google Api Client: connection completed')

class SpreadSheetsClient(GoogleApiClient):
    def __init__(self,
            developer_api_key: str = None,
            credentials_oauth2: str = None,
            token_json: str = None,
            readonly: bool = False,
        ):
        scopes = []
        if readonly:
            scopes.append("https://www.googleapis.com/auth/spreadsheets.readonly")
        else:
            scopes.append("https://www.googleapis.com/auth/spreadsheets")
        
        super().__init__(
            discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4',
            developer_api_key = developer_api_key,
            credentials_oauth2 = credentials_oauth2,
            token_json = token_json,
            scopes=scopes,
        )
        
        self._spreadsheets_service = self._service.spreadsheets()
    
    def new_spreadsheets(self, spreadsheets_id: str) -> SpreadSheets:
        return SpreadSheets(self._spreadsheets_service, spreadsheets_id)

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SAMPLE_SPREADSHEET_ID = '16Mv67GBqUqwHYQoZ8KBz4T-QegDzRP9MwOXKP4l1ymY'
EVENTS_SHEET_NAME = 'Event Cards'
PLAGUE_SHEET_NAME = 'Plague Cards'
CHARACTERS_SHEET_NAME = 'Character Cards'
TRIUMPHS_SHEET_NAME = 'Triumph Cards'
INDEX_TO_LETTER_MAP = {k: v for k, v in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])}


_sheet = None


def _init():
  global _sheet
  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)

    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)

  service = build('sheets', 'v4', credentials=creds)

  _sheet = service.spreadsheets()


def _get_sheet():
  global _sheet
  if not _sheet:
    _init()
  return _sheet


def _create_range_string(sheet_name, start_row_id, end_row_id, start_column_id=0, end_column_id=0):
  result = "'{0}'!{1}{2}:{3}{4}".format(sheet_name, INDEX_TO_LETTER_MAP[start_column_id], start_row_id, INDEX_TO_LETTER_MAP[end_column_id], end_row_id)
  return result


def get_range(sheet_name, start_row_id, end_row_id, start_column_id=0, end_column_id=0):
  result = _get_sheet().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    range=_create_range_string(sheet_name, start_row_id, end_row_id, start_column_id, end_column_id),
    valueRenderOption='FORMATTED_VALUE').execute()
  values = result.get('values', [])

  if not values:
      print('No data found.')
  else:
      return values
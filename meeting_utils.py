from datetime import datetime, timedelta, timezone
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from log_utils import print_in_file

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]

def construire_rendezvous(nom: str, endroit: str, debut: datetime, duree: float, description: str | None = None):
    fin = (debut + timedelta(hours=duree)).astimezone(timezone.utc).isoformat('T')
    event = {
        'summary': nom,
        'location': endroit,
        'description': description if description else '',
        'start': {
            'dateTime': debut.astimezone(timezone.utc).isoformat("T"),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': fin,
            'timeZone': 'America/Los_Angeles',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    return event

"""
  Code repris depuis l'api de base de google
"""
def envoyer_rendezvous(rendez_vous):
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  
  try:
    service = build("calendar", "v3", credentials=creds)

    rendez_vous = service.events().insert(calendarId='primary', body=rendez_vous).execute()
    print_in_file('Event created: %s' % (rendez_vous.get('htmlLink')))
    return "Event created"

  except HttpError as error:
    print_in_file(f"[HTTP RDV] An error occurred: {error}")
    return None

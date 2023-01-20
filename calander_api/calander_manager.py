from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
from datetime import datetime, timedelta
import hashlib

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"
ATTENDES_PATH = "attendes.txt"

DELIMITER = ": "
MENORA_HASH = 'menora_hash' + DELIMITER
MENORA_SPOT = "מנורה מבטחים הסיוט הכי גדול"

EVENT_TIME = timedelta(minutes=30)
SEARCH_TIME = timedelta(days=31)
TIME_ZONE = 'Israel'

REMINDERS = [{'method': 'popup', 'minutes': 60 * 24},
             {'method': 'popup', 'minutes': 60}]

class Event:
    def __init__(self, event_json):
        assert 'id' in event_json, "No id in event json, %s" % event_json
        assert "description" in event_json, "No description in event json, %s" % event_json
        assert MENORA_HASH in event_json['description'], "Menora hash no present in event, %s" % event_json

        self.id = event_json['id']
        self.hash = event_json['description'].split(": ")[1].strip()
    
    def __str__(self) -> str:
        return "%s - %s" % (self.id, self.hash)
    
    def get_id(self) -> str:
        return self.id
    
    def get_hash(self) -> str:
        return self.hash

def create_hash(desc: str, time: datetime) -> str:
    return hashlib.md5((desc+str(time)).encode("utf-8")).hexdigest()

class CalanderManager:

    def __init__(self, secret_folder: str): # May through http error, all of them
        self.generate_service(os.path.join(secret_folder, TOKEN_PATH), os.path.join(secret_folder, CREDENTIALS_PATH))
        self.attendes = []
        with open(os.path.join(secret_folder, ATTENDES_PATH), "r") as f:
            for attende in f:
                self.attendes.append({'email': attende.strip()})

    def generate_service(self, token_path: str, credentials_path: str):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)

    def get_all_events(self) -> List[Event]:
        request_result = self.service.events().list(calendarId='primary', q=MENORA_SPOT).execute()

        assert 'items' in request_result, "No items field in request result"
        return [Event(event) for event in request_result['items']]

    def delete_event(self, event: Event):
        self.service.events().delete(calendarId='primary', eventId=event.get_id()).execute()
    
    def add_menora_event(self, desc: str, time: datetime):
        menora_hash = MENORA_HASH + "\n%s" % create_hash(desc, time)
        event = {
                    'summary': desc,
                    'location': MENORA_SPOT,
                    'description': menora_hash,
                    'start': {
                        'dateTime': time.isoformat(),
                        'timeZone': TIME_ZONE,
                    },
                    'end': {
                        'dateTime': (time + EVENT_TIME).isoformat(),
                        'timeZone': TIME_ZONE,
                    },
                    'attendees': self.attendes,
                    'reminders': {
                        'useDefault': False,
                        'overrides': REMINDERS,
                    },
                }
        
        self.service.events().insert(calendarId='primary', body=event).execute()


if __name__ == '__main__':
    manager = CalanderManager(TOKEN_PATH, CREDENTIALS_PATH)
import os

# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
# import pickle

import datetime

from google.oauth2 import service_account
import googleapiclient.discovery as discovery

class MarengueCal:
    def __init__(self):
        self.service = self.build_service()
        self.cal_events = dict()
        self.calId = 'marenguecal@gmail.com'
        self.all_events = None
        self.take_all_events()
        
    def build_service(self):
        SCOPE = 'https://www.googleapis.com/auth/calendar'
        # CLIENT_SECRET_FILE = 'marengue/secret.json'
        if os.path.exists('secret.json'):
            CLIENT_SECRET_FILE = 'secret.json'
        else:
            CLIENT_SECRET_FILE = 'marengue/secret.json'
        creds = service_account.Credentials.from_service_account_file(CLIENT_SECRET_FILE)
        creds_with_scope = creds.with_scopes([SCOPE])
        return discovery.build('calendar', 'v3', credentials=creds_with_scope)

    def take_all_events(self, calendar_id = None):
        if calendar_id is None:
            calendar_id = self.calId
        self.all_events = self.service.events().list(
            calendarId=calendar_id,
            showDeleted=True
            ).execute()

    @property
    def sync_token(self):
        synced_token = None
        if os.path.exists('sync_token'):
            with open('sync_token', 'r') as token_in_file:
                synced_token = token_in_file.read()
        
        return synced_token

    def set_sync_token(self, token):
        with open('sync_token', 'w') as token_in_file:
            token_in_file.write(token)

    def print_all_events(self):
        ev = self.all_events
        items = ev['items']
        updated = str(datetime.datetime.fromisoformat(
            ev['updated'].split('Z')[0]))[:10]
        print(f'calendar: {ev["summary"]}, updated: {updated}')
        print('-----------------------------------------')
        for item in items:
            summary = item.get('summary', 'Nope')[:12]
            description = item.get('description', 'Nope')[:12]
            location = item.get('location', 'Nope')[:12]
            start_ = item['start'].get('dateTime', 'Nope')
            start_date = datetime.datetime.fromisoformat(start_)
            date = start_date.strftime('%y%m%d %H:%M')
            end_ = item['end'].get('dateTime', 'Nope')
            end_date = datetime.datetime.fromisoformat(end_)
            duration = (end_date - start_date).seconds // 60
            status_dict = {'confirmed':'V','cancelled': 'X'}
            status = status_dict[item['status']]
            eventId = item['id'][:8]
            updated_date = datetime.datetime.fromisoformat(item['updated'].split('Z')[0])
            updated = updated_date.strftime('%m-%d %H:%M:%S')
            
            print(f'[{status}]{date}/{duration} [{eventId}]{updated} {location} {summary} {description}')

    def marengue_sync_elements(self) -> dict:
        ev = self.all_events
        updated = datetime.datetime.fromisoformat(ev['updated'].split('Z')[0])

        events_sum = {
            'calendar': ev['summary'],
            'updated': updated,
            'nextSyncToken': ev['nextSyncToken']
        }

        return events_sum

    def marengue_token_events_list(self, token=None, calendar_id=None):
        if calendar_id is None:
            calendar_id = self.calId
        if token is None:
            token = self.sync_token
        response = self.service.events().list(
            calendarId=calendar_id,
            syncToken=token,
            ).execute()
        self.set_sync_token(response['nextSyncToken'])
        return response

    def marengue_all_events_list(self) -> list:
        items = self.all_events['items']
        events_store = []
        for item in items:
            summary = item.get('summary', 'Nope')
            description = item.get('description', 'Nope')
            location = item.get('location', 'Nope')
            start_ = item['start'].get('dateTime', 'Nope')
            start_date = datetime.datetime.fromisoformat(start_)
            date = start_date.strftime('%y%m%d %H:%M')
            end_ = item['end'].get('dateTime', 'Nope')
            end_date = datetime.datetime.fromisoformat(end_)
            duration = (end_date - start_date).seconds // 60
            status_dict = {'confirmed': 'V', 'cancelled': 'X'}
            status = status_dict[item['status']]
            eventId = item['id'][:8]
            updated_date = datetime.datetime.fromisoformat(item['updated'].split('Z')[0])
            updated = updated_date.strftime('%m-%d %H:%M:%S')

            events_store.append({
                'id': item['id'],
                'location': location,
                'summary': summary,
                'description': description,
                'start': start_date,
                'duration': duration,
                'google_status': status,
                'updated': updated_date,
            })

        return events_store

    def count_events(self):
        all_events = self.cal_events.values()
        if not all_events:
            print('No upcoming events found.')
        count = 0
        for events in all_events:
            for event in events:
                if 'summary' in event:
                    # if 'PTO' in event['summary']:
                    count += 1
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(start, event['summary'])
        print('Total events is %d' % count)

    def take_id_marengue(self):
        events = self.cal_events['marenguecal@gmail.com']

        for event in events:
            if event['summary']:
                print(event['id'], event['summary'])
            else:
                print(event['id'], 'not summary')

    def get_event_from_marengue(self, event_id, calendar_id=None):
        if calendar_id is None:
            calendar_id = self.calId
        response = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
            ).execute()
        return response

    def add_event_to_marengue(
        self,
        summary, location, description,
        start_date, end_date, status):


        event_body = {
          'summary': summary,
          'location': location,
          'description': description,
          'status': status,
          'start': {
            'dateTime': start_date.isoformat(),
          },
          'end': {
            'dateTime': end_date.isoformat(),
          }
        }

        response = self.service.events().insert(
            calendarId=self.calId,
            body=event_body
            ).execute()

        return response

    def update_event_to_merengue(self, event_id,
                              summary, location, description,
                              start_date, end_date, status):
        

        event_body = {
          'summary': summary,
          'location': location,
          'description': description,
          'status': status,
          'start': {
            'dateTime': start_date.isoformat(),
          },
          'end': {
            'dateTime': end_date.isoformat(),
          }
        }

        response = self.service.events().update(
            calendarId=self.calId,
            eventId=event_id,
            body=event_body,
            ).execute()

        return response

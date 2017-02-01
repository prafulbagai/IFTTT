from __future__ import division
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from datetime import datetime as dt
import httplib2


class Gmail(object):

    def __init__(self, access_token=None):
        self.credentials = AccessTokenCredentials(access_token, user_agent='')
        self._http = self.credentials.authorize(httplib2.Http())
        self.gmail_service = build('gmail', 'v1', http=self._http)

    def get_messages(self, msg_ids=[]):
        results = dict()
        for m_id in msg_ids:
            msg = self.gmail_service.users().messages().get(userId='me',
                                                            id=m_id).execute()
            if msg:
                headers = msg.get('payload').get('headers')
                temp = dict()
                for i in headers:
                    if i.get('name') in ['Subject', 'To', 'From']:
                        temp[i.get('name')] = i.get('value')
                temp['snippet'] = msg.get('snippet')
                temp['datetime'] = msg.get('internalDate')
                temp['datetime'] = dt.fromtimestamp(int(temp['datetime']) // 1000)
                if temp['From'] in results:
                    results[temp['From']].append(temp)
                else:
                    results[temp['From']] = [temp]
        return results

    def get_list_of_msgid(self, epoch_after='', emails=[], msg_type='unread'):
        ''' epoch_after : epoch in sec and get message after this epoch
            emails: list of emails
            is:unread AND after:epoch_after AND (email1 OR email2)
        '''
        query = 'is:' + msg_type
        if epoch_after:
            query += ' AND after:' + epoch_after

        if emails:
            q2 = ' OR '.join(['from:' + str(i) for i in emails])
            query += ' AND (' + q2 + ' )'

        results = self.gmail_service.users().messages().list(userId='me',
                                                             q=query).execute().get('messages', [])
        msg_ids = [message.get('id') for message in results]
        return self.get_messages(msg_ids=msg_ids)

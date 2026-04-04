from gmail_client import create_gmail_service
from datetime import datetime
import math
import base64
from bs4 import BeautifulSoup


now = datetime.now()
timestamp = math.floor(datetime.timestamp(now))
service = create_gmail_service()

def get_recent_emails(service, timestamp):
    return service.users().messages().list(maxResults=5,userId='me',q='in:inbox before:{}'.format(timestamp)).execute()
    

def get_email_details():

    results = get_recent_emails(service, timestamp)
    messages = results.get('messages')
    EmailRecepit=[]
    count=1
    for msg in messages:
        print("Count",count)
        count+=1
        # Get the message from its id

        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']
        print(f"Payload: {payload}")
        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        if 'parts' in payload:
          
       
            for part in payload['parts']:
        
                if part['mimeType'] == 'text/html' and part['body'] and part['body']['data']:
                    data = part['body']['data']
                    data = data.replace("-","+").replace("_","/")
                    decoded_data = base64.b64decode(data)
                    # print(f"Decoded data: type{type(decoded_data)}")
                    # Now, the data obtained is in lxml. So, we will parse 
                    # it with BeautifulSoup library
                    # soup = BeautifulSoup(decoded_data , "lxml")
                    # body = soup.body()

                    body = decoded_data.decode('utf-8')

                    # Printing the subject, sender's email and message
                    print("Subject: ", subject)
                    print("From: ", sender)
                    print("Message: ", body)
                    print('\n')
       
    # print(results)
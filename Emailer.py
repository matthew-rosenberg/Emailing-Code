from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from csv import reader
from typing import List
import re 
from random import randint
from time import sleep

# https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
def check_email(email):  
    # Make a regular expression for validating an Email 
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return True          
    else:  
        return False

def read_csv(fp:str) -> List[List[str]]:
    # read csv file as a list of lists
    with open(fp, 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        # Pass reader object to list() to get a list of lists
        list_of_rows = list(csv_reader)
    return list_of_rows

def read_file(fp:str) -> str:
    with open(fp, 'r') as file:
        message_text = file.read()
        return message_text

#https://developers.google.com/gmail/api/guides/sending
#https://developers.google.com/gmail/api/auth/web-server
def get_creds():
    """
    This is the method for getting the credentials and access to the gmail account.
    The file token.pickle stores the user's access and refresh tokens, and is created automatically when the 
    authorization flow completes for the first time.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send'] #https://developers.google.com/gmail/api/auth/scopes
    #scopes = how much access you need to the account
    creds = None
    if os.path.exists('token.pickle'): #If we already have an access token
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file( #file that is downloadaed from google account before starting
                'credentials.json', SCOPES) #https://developers.google.com/gmail/api/quickstart/python
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text, name=None, verbose=True):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  if name:
    from_str = f"{name} <{sender}>" #https://stackoverflow.com/questions/44385652/add-senders-name-in-the-from-field-of-the-email-in-python
  else:
    from_str = sender
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = from_str
  message['subject'] = subject
  if verbose:
    print(f"Message to {message['to']} from {message['from']} with subject {message['subject']}")
  b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
  b64_string = b64_bytes.decode()
  return {'raw': b64_string} 
    #https://stackoverflow.com/questions/46668084/how-do-i-properly-base64-encode-a-mimetext-for-gmail-api, why decode and encode

def send_message(service, user_id, message, verbose=True):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    if verbose:
      print (f"Message Id: {message['id']}")
    return message

def main():
    #constants
    sender = "mattjayrosenberg@gmail.com"
    name = "Matthew Rosenberg"
    fp = r"Agencies.csv"
    subject = "Kosher Certification Recognizer App"

    contacts = read_csv(fp)
    service = get_creds()

    for contact in contacts:
        email, recipient_name = contact
        sleep(randint(1,4))
        if check_email(email):
          to = email
          message_text = f"Hi {recipient_name},\n\nMy name is Matthew Rosenberg and I'm a senior in Columbia's engineering school and the current student president of the Hillel executive board at Columbia. I, along with another Jewish student here, are working on an app that would help identify the certifications of the different Kashrut agencies. You would be able to scan a symbol on a food item, and it would identify for you the agency behind that symbol, so you can decide if that kashrut is stringent enough for you. There was a similar app on the iPhone app store called The Kosher App, but we are taking it over and updating the machine learning model it uses. We are in the process of gathering data on the different agencies, and we wanted to know if you had images of your certification symbol on different food items that we could use for training data for our neural network image classification model. The more pictures the better as it will take hundreds or thousands of each symbol to operate properly and we as two college students don't have the time or resources to take all those pictures ourselves. Any advice, images, or data would be appreciated!\n\nThanks so much,\nMatthew Rosenberg"
          mes = create_message(sender, to, subject, message_text, name)
          send_message(service, "me", mes,verbose=False)
        else:
          print(f"Invalid email {email}") 

if __name__ == "__main__":
   main()
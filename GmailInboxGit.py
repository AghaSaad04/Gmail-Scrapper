from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import re
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
import csv
import sys


non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

# Creating a storage.JSON file with authentication details
SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # we are using modify and not readonly, as we will be marking the messages Read
store = file.Storage('storage.json') 
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

user_id =  'me'
label_id_one = 'INBOX'
label_id_two = 'UNREAD'
mssg_list = []
temp_dict = []

# Getting all the unread messages from Inbox
# labelIds can be changed accordingly
unread_msgs = GMAIL.users().messages().list(userId='me',labelIds=label_id_one,q="category:primary",maxResults="10000").execute()
mssg_list = unread_msgs['messages']
print ("Total unread messages in inbox: ", str(len(mssg_list)))

while 'nextPageToken' in unread_msgs:
        page_token = unread_msgs['nextPageToken']
        unread_msgs = GMAIL.users().messages().list(userId='me',labelIds=label_id_one,q="category:primary",maxResults="10000",pageToken=page_token).execute()
        print (type(mssg_list))
        mssg_list.extend(unread_msgs['messages'])
# We get a dictonary. Now reading values for the key 'messages'

print ("Total unread messages in inbox: ", str(len(mssg_list)))

final_list = []

count = 0
for mssg in mssg_list:
    tmp_dict = {}
    m_id = mssg['id'] # get id of individual message
    message = GMAIL.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
    payld = message['payload'] # get payload of the message 
    headr = payld['headers'] # get header of the payload

    for three in headr: # getting the Sender
        if three['name'] == 'From':
            msg_from = three['value']
            msg_from = msg_from.split(" <")
            try:
                name = msg_from[0]
            except:
                print("")
            try:
                email = msg_from[1]
            except:
                pass
            count = count+1
            print (count)
            #print (name)
            email = email.replace('<','')
            email = email.replace('>','')
            sender = name + ":" +email
            #print (email)
            #print (temp_dict)
            if sender not in temp_dict:
                #print("hi")
                temp_dict.append(sender)
            
        else:
            pass

    #temp_dict['Snippet'] = message['snippet'] # fetching message snippet


    try:
        
        # Fetching message body
        mssg_parts = payld['parts'] # fetching the message parts
        part_one  = mssg_parts[0] # fetching first element of the part 
        part_body = part_one['body'] # fetching body of the message
        part_data = part_body['data'] # fetching data from the body
        clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
        clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
        soup = BeautifulSoup(clean_two , "lxml" )
        mssg_body = soup.body()
        # mssg_body is a readible form of message body
        # depending on the end user's requirements, it can be further cleaned 
        # using regex, beautiful soup, or any other method
        #temp_dict['Message_body'] = mssg_body

    except :
        pass

    #print (temp_dict.translate(non_bmp_map))

     # This will create a dictonary item in the final list
    
    # This will mark the messagea as read
    #GMAIL.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
    

final_str="Name,Email\n"
for index in range(len(temp_dict)):
    final_str=final_str+temp_dict[index].replace(':',',')+"\n"
    #tmp_dict['Name'] , tmp_dict['Email'] = temp_dict[index].split(":")
    #print (tmp_dict['Name'])
    #print (tmp_dict['Email'])
    #print (final_list)
    #final_list.append(tmp_dict)
    #print (final_list)
#print ("Total messaged retrived: ", str(len(final_list)))

'''
The final_list will have dictionary in the following format:
{	'Sender': '"email.com" <name@email.com>', 
	'Subject': 'Lorem ipsum dolor sit ametLorem ipsum dolor sit amet', 
	'Date': 'yyyy-mm-dd', 
	'Snippet': 'Lorem ipsum dolor sit amet'
	'Message_body': 'Lorem ipsum dolor sit amet'}
The dictionary can be exported as a .csv or into a databse
'''

#exporting the values as .csv
##with open('CSV_NAME.csv', 'w', encoding='utf-8', newline = '') as csvfile: 
f = open("CSV_NAME.csv", "w")
f.write(final_str)
f.close()
##    fieldnames = ['Name','Email']
##    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter = ',')
##    writer.writeheader()
##    for val in final_list:
##        writer.writerow(val)

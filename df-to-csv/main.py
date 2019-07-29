# Initial example is from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/functions/http/main.py

import time
import json
import random
import datetime
# from http.server import *
# from urllib.parse import urlparse
import os
from werkzeug.utils import secure_filename
import tempfile
import zipfile
import shutil
import glob
import pandas as pd
import numpy as np

from flask import send_file, jsonify

# from cgi import parse_header, parse_multipart
import pickle
from googleapiclient.discovery import build
from googleapiclient import discovery

    
# upload
path_to_credentials = 'token.pickle'
with open(path_to_credentials, 'rb') as token:
    credentials = pickle.load(token)
service = build('drive', 'v3', credentials=credentials)

path_to_credentials = 'token.pickle'
with open(path_to_credentials, 'rb') as token:
    credentials = pickle.load(token)
    print(credentials)
service_sheets = discovery.build('sheets', 'v4', credentials=credentials)


def rreplace(s, old, new, count=1):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]
    
def escape_curly_braces(text):
    return text.replace("}", "\\}").replace("{", "\\{")  # use of blackslash problematic


def create_spreadsheets():
    create_spreadsheet_body = {
      "properties": {
        "title": "dialogflow-converted"+generateRandomHex()[:8]
      }
    }

    create_request = service_sheets.spreadsheets().create(body=create_spreadsheet_body)
    create_response = create_request.execute()
    return create_response["spreadsheetId"]

    

def make_tab(SPREADSHEET_ID, tab_name):
    body = {
      "requests": [
        {
          "addSheet": {
            "properties": {
              "title": tab_name
            }
          }
        }
      ]
    }
    
    request = service_sheets.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
    response = request.execute()
    return response

def delete_default_tab(SPREADSHEET_ID):
    body = {
      "requests": [
        {
          "deleteSheet": {
            "sheetId": 0
          }
        }
      ]
    }
    
    request = service_sheets.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
    response = request.execute()
    return response


# routine to make public
def make_public_callback(request_id, response, exception):
    if exception:
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))

        
def make_public(file_id):
    batch = service.new_batch_http_request(callback=make_public_callback)

    user_permission = {
        'type': 'anyone',
        'role': 'writer',
    }

    batch.add(service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
    ))
    
    batch.execute()


# convenience routines
def find_sheet_id_by_name(SPREADSHEET_ID, sheet_name):
    # ugly, but works
    
    sheets_with_properties = service_sheets \
        .spreadsheets() \
        .get(spreadsheetId=SPREADSHEET_ID, fields='sheets.properties') \
        .execute() \
        .get('sheets')

    for sheet in sheets_with_properties:
        if 'title' in sheet['properties'].keys():
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']


def push_csv_to_gsheet(SPREADSHEET_ID, csv_path, sheet_id):
    with open(csv_path, 'r', encoding='utf-8') as csv_file:
        csvContents = csv_file.read()
    body = {
        'requests': [{
          "updateCells": {
            "range": {
              "sheetId": sheet_id
            },
            "fields": "userEnteredValue"
          }
        },{
            'pasteData': {
                "coordinate": {
                    "sheetId": sheet_id,
                    "rowIndex": "0",  # adapt this if you need different positioning
                    "columnIndex": "0", # adapt this if you need different positioning
                },
                "data": csvContents,
                "type": 'PASTE_NORMAL',
                "delimiter": ',',
            }
        }]
    }
    
    request = service_sheets.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
    response = request.execute()
    return response

    
def generateRandomHex():
    datetime_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
    return datetime_string + '%08x' % random.randrange(16**8)


def generate_ID():
    c = ["".join([random.choice('01234567890abcdef') for _ in range(4)]) 
         for _ in range(8)]
    return c[0]+c[1]+"-"+c[2]+"-"+c[3]+"-"+c[4]+"-"+c[5]+c[6]+c[7]


def create_csv(FILE_NAME):

    rand_string = generate_ID()
    # please test this code
    # - "_usersays" multiple times
    # - "!!!" multiple times
    files = glob.glob('/tmp/{}/intents/*.json'.format(FILE_NAME))
    files = [file.replace("!!!", rand_string) for file in files]  
    files = [file.replace(".json","!!!!<<.json>>!!!!") for file in files]  
    files = [rreplace(file, "_usersays","!!!<<usersays>>!!!") for file in files]  
    files = sorted([intent for intent in files])
    files = [file.replace("!!!<<usersays>>!!!","_usersays") for file in files]  
    files = [file.replace("!!!!<<.json>>!!!!",".json") for file in files]
    files = [file.replace(rand_string,"!!!") for file in files]  
    # files.remove('template/intents/Default Fallback Intent.json')


    # In[5]:


    # does not assume that all intents have usersays
    # assume English only
    intent_hold = "none"
    intent_jsons = []
    for file in files:
        intent_name = file.rpartition('.')[0]
        if not intent_name.startswith(intent_hold + "_usersays"):   # Some intent names are prefix of another #14
            intent_jsons.append([file])  #15
            intent_hold = intent_name
        else:
            intent_jsons[-1].append(file)


    # In[6]:


    intents = []
    for intent_json in intent_jsons:
    #     try:
            print(intent_json)
            intent = {}
            intent_info_json = intent_json[0]
            usersays_jsons = intent_json[1:] # should be one only

            with open(intent_info_json, encoding="utf-8") as f:
                intent_info = json.load(f)
            
            intent["INTENT_NAME"] = intent_info["name"]
            intent["INPUT_CONTEXT"] = intent_info["contexts"]
            intent["OUTPUT_CONTEXT"] = [str(c["lifespan"]) + ", " + str(c["name"])  
                                        for c in intent_info["responses"][0]["affectedContexts"]]
            intent["PARAMS"] = ""
            if "parameters" in intent_info["responses"][0]:
                intent["PARAMS"] = json.dumps(intent_info["responses"][0]["parameters"])
            
            intent["RESPONSES"] = []
            # print(intent_info) - may not be able to print unicode strings
            if "messages" in intent_info["responses"][0]:  # may not have "messages"
                for message in intent_info["responses"][0]["messages"]:
                    if message["type"] == 0:
                        if type(message["speech"]) == list:
                            intent["RESPONSES"].append(message["speech"])
                        else:
                            intent["RESPONSES"].append([message["speech"]])
                    elif message["type"] == 4:
                        intent["RESPONSES"].append([json.dumps(message["payload"])])
                    else:
                        pass
        #         print()
            
            intent["USER_SAYS"] = []
            for usersays_json in usersays_jsons: # should be one or none
                with open(usersays_json, encoding="utf-8") as f:
                    usersays_info = json.load(f)
                for usersay in usersays_info:
                    usersay_str = ""
                    for usersay_chunk in usersay["data"]:
                        if "text" not in usersay_chunk:
                            # It could have been {"userDefined": false}
                            continue
                        text = usersay_chunk["text"]
                        text = escape_curly_braces(text)
                        if "alias" not in usersay_chunk:
                            usersay_chunk["alias"] = ""
                        if "meta" in usersay_chunk:
                            usersay_str += "{" + usersay_chunk["meta"] + "," + usersay_chunk["alias"] +  "," + text + "}"
                        else:
                            usersay_str += text
                    intent["USER_SAYS"].append(usersay_str)
            intents.append(intent)
        #     pp(intent_info)
        #     break
    #     except:
    #         pass



    # In[7]:


    MAX_TOTAL_RESPONSES = max([len(intent["RESPONSES"]) for intent in intents]+[1])
    # create empty arrays until they have the same number of arrays
    for intent in intents:
        for _ in range(MAX_TOTAL_RESPONSES - len(intent["RESPONSES"])):
            intent["RESPONSES"].append([])
        pass


    # In[8]:


    intents


    # In[9]:


    len_INPUT_CONTEXT = max([len(intent["INPUT_CONTEXT"]) for intent in intents]+[1])
    len_OUTPUT_CONTEXT = max([len(intent["OUTPUT_CONTEXT"]) for intent in intents]+[1])
    len_USER_SAYS = max([len(intent["USER_SAYS"]) for intent in intents]+[1])
    lens_RESPONSES = []  # find out the max number of variants of the i-th response
    for i in range(MAX_TOTAL_RESPONSES):
        lens_RESPONSES.append(max([len(intent["RESPONSES"][i]) for intent in intents]+[1]))
    lengths = [2, len_INPUT_CONTEXT, len_OUTPUT_CONTEXT, len_USER_SAYS, *lens_RESPONSES]


    # In[10]:


    row_length = sum(lengths)
    columns = [""]*row_length
    columns[0] = "INTENT_NAME"
    columns[1] = "PARAMS"
    columns[sum(lengths[:1])] = "INPUT_CONTEXT"
    columns[sum(lengths[:2])] = "OUTPUT_CONTEXT"
    columns[sum(lengths[:3])] = "USER_SAYS"
    for i in range(MAX_TOTAL_RESPONSES):
        columns[sum(lengths[:4+i])] = "RESPONSES"

    # In[11]:


    row_list = []
    for intent in intents:
        row = [np.nan]*row_length
        row[0] = intent["INTENT_NAME"]
        row[1] = intent["PARAMS"]
        row[sum(lengths[:1]):sum(lengths[:1])+len(intent["INPUT_CONTEXT"])] = intent["INPUT_CONTEXT"]
        row[sum(lengths[:2]):sum(lengths[:2])+len(intent["OUTPUT_CONTEXT"])] = intent["OUTPUT_CONTEXT"]
        row[sum(lengths[:3]):sum(lengths[:3])+len(intent["USER_SAYS"])] = intent["USER_SAYS"]
        for i in range(MAX_TOTAL_RESPONSES):
            row[sum(lengths[:4+i]):sum(lengths[:4+i])+len(intent["RESPONSES"][i])] = intent["RESPONSES"][i]
        row_list.append(row)

    # In[12]:


    df = pd.DataFrame(row_list, columns=columns)
    df


    # In[13]:


    df.to_csv("/tmp/{}.csv".format(FILE_NAME))


    #######################################################################################

    # In[6]:

    # please test this code
    # - "_entries" multiple times
    # - "!!!" multiple times
    files = glob.glob('/tmp/{}/entities/*.json'.format(FILE_NAME, FILE_NAME))
    files = [file.replace("!!!", rand_string) for file in files]  
    files = [file.replace(".json","!!!!<<.json>>!!!!") for file in files]  
    files = [rreplace(file, "_entries","!!!<<entries>>!!!") for file in files]  
    files = sorted([intent for intent in files])
    files = [file.replace("!!!<<entries>>!!!","_entries") for file in files]  
    files = [file.replace("!!!!<<.json>>!!!!",".json") for file in files]
    files = [file.replace(rand_string,"!!!") for file in files]  


    # In[7]:


    # assume English only
    entity_hold = "none"
    entity_jsons = []
    for file in files:
        entity_name = file.rpartition('.')[0]
        if not entity_name.startswith(entity_hold + "_entries"):  # entities pairing is also problematic #16
            entity_jsons.append([file])
            entity_hold = entity_name
        else:
            entity_jsons[-1].append(file)
    entity_jsons


    # In[8]:

    # change variable names please - BAD NAMING
    entities = []
    for entity_json in entity_jsons:
    #     try:
            print(entity_json)
            entity = {}
            entity_info_json = entity_json[0]
            usersays_jsons = entity_json[1:] # could be different from one only

            with open(entity_info_json, encoding="utf-8") as f:
                entity_info = json.load(f)

            entity["ENTITY_NAME"] = entity_info["name"]
            entity_info_copy = entity_info
            del entity_info_copy["name"]
            entity["PARAMS"] = str(entity_info_copy)
            entity["ENTRIES"] = []
            
            for usersays_json in usersays_jsons: # could be different from one only
                with open(usersays_json, encoding="utf-8") as f:
                    usersays_info = json.load(f)
                for usersay in usersays_info:
                    entity["ENTRIES"].append({usersay['value']:usersay['synonyms']})
            
            entities.append(entity)
    #     except:
    #         pass
    # In[9]:


    entities


    # In[10]:


    row_list = []
    for entity in entities:
        entity_name = entity["ENTITY_NAME"]
        entity_property = entity["PARAMS"]
        for entries in entity["ENTRIES"]:
            row = [entity_name, entity_property]
            for key, value in entries.items():
                row += [key]
                row += value
                # the entity_name and entity_property only appears in the first row
                entity_name = ""
                entity_property = ""
                break
            row_list.append(row)


    # In[11]:


    max_len = max([4] + [len(row) for row in row_list])

    columns = ["ENTITY_NAME", "PARAMS", "ENTITY_VALUE", "SYNONYMS"] + [""]*(max_len-4)
    for i,row in enumerate(row_list):
        row_list[i] = row + [""]*(max_len-len(row))


    # In[12]:


    df = pd.DataFrame(row_list, columns=columns)
    df


    # In[13]:


    df.to_csv("/tmp/{}-ent.csv".format(FILE_NAME))


    #######################################################################################


    def json_to_csv(json_dict):
        csv_list = []
        for k,v in json_dict.items():
            csv_list.append([k,str(type(v)).split("\'")[1],str(v)])
        return csv_list

    # import ast
    # 
    # def csv_to_json(csv_list):
    #     '''csv_list is a list of lists
    #     [['key', 'type', 'value represented as string']]'''
    #     json_dict = {}
    #     for p in csv_list:        
    #         if p[1] == 'float':
    #             value = float(p[2])
    #         elif p[1] == 'int':
    #             value = int(p[2])
    #         elif p[1] == 'bool':
    #             value = (p[2] != "True")
    #         elif p[1] == 'dict' or p[1] == 'list':
    #             value = ast.literal_eval(p[2])
    #         elif p[1] == 'str':
    #             value = p[2]
    #         else:
    #             value = ""
    #             print("ERROR, how is this possible?")
    #         json_dict[p[0]] = value
    #     return json_dict


    with open('/tmp/{}/agent.json'.format(FILE_NAME), encoding="utf-8") as f:
        agent_info = json.load(f)
        
    agent_csv = json_to_csv(agent_info)
    df_agent = pd.DataFrame(agent_csv, columns=["key", "value-type", "value-string"])
    df_agent.to_csv("/tmp/{}-agent.csv".format(FILE_NAME), index=False)



# Helper function that computes the filepath to save files to
def get_file_path(filename):
    # Note: tempfile.gettempdir() points to an in-memory file system
    # on GCF. Thus, any files in it must fit in the instance's memory.
    file_name = secure_filename(filename)
    return os.path.join(tempfile.gettempdir(), file_name)


def df_to_csv(request):
    """ Parses a 'multipart/form-data' upload request
    This function show how you can 
    - receive zipfile from form-data
    - unzip the zipfile into in-memory /tmp
    - zip to make a zipfile in /tmp
    - return the zipfile to the requestor
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
         Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    # This code will process each non-file field in the form
    fields = {}
    data = request.form.to_dict()
    for field in data:
        fields[field] = data[field]
        print('Processed field: {} : {}'.format(field, data[field]))

    # This code will process each file uploaded
    files = request.files.to_dict()
    for file_name, file in files.items():
        file.save(get_file_path(file_name))
        print('Processed file: %s' % file_name)

    FILE_NAME = generateRandomHex()
    print(FILE_NAME)

    # Clear temporary directory
    for file_name in files:
        file_path = get_file_path(file_name)
        file_path_zipfile = zipfile.ZipFile(file_path)
        file_path_zipfile.extractall(path='/tmp/{}'.format(FILE_NAME))
        os.remove(file_path)
    
    create_csv(FILE_NAME)

    files_list = os.listdir('/tmp')
    for file_in_list in files_list:
        print(file_in_list)

    for file_in_list in os.listdir('/tmp/{}'.format(FILE_NAME)):
        print(file_in_list)

    for file_in_list in os.listdir('/tmp/{}/intents'.format(FILE_NAME)):
        print(file_in_list)

    SPREADSHEET_ID = create_spreadsheets()
    make_tab(SPREADSHEET_ID, "intents")
    make_tab(SPREADSHEET_ID, "entities")
    make_tab(SPREADSHEET_ID, "properties")
    delete_default_tab(SPREADSHEET_ID)
    make_public(SPREADSHEET_ID)        

    print("SPREADSHEET_ID", SPREADSHEET_ID)

    push_csv_to_gsheet(
        SPREADSHEET_ID=SPREADSHEET_ID,
        csv_path="/tmp/{}.csv".format(FILE_NAME),
        # csv_path="/tmp/z-intents.csv",
        sheet_id=find_sheet_id_by_name(SPREADSHEET_ID,"intents")
    )

    push_csv_to_gsheet(
        SPREADSHEET_ID=SPREADSHEET_ID,
        csv_path="/tmp/{}-ent.csv".format(FILE_NAME),
        # csv_path="/tmp/z-entities.csv",
        sheet_id=find_sheet_id_by_name(SPREADSHEET_ID,"entities")
    )
    
    push_csv_to_gsheet(
        SPREADSHEET_ID=SPREADSHEET_ID,
        csv_path="/tmp/{}-agent.csv".format(FILE_NAME),
        # csv_path="/tmp/z-properties.csv",
        sheet_id=find_sheet_id_by_name(SPREADSHEET_ID,"properties")
    )
    
    print(SPREADSHEET_ID)
    
    sheets_link = "https://docs.google.com/spreadsheets/d/" + SPREADSHEET_ID

    print(credentials)
    print(sheets_link)
    shutil.make_archive("/tmp/combined", 'zip', "/tmp/")
    response = jsonify({"sheets_link" : sheets_link})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
# [END functions_http_form_data]


if __name__ == "__main__":
    from flask import Flask, request
    app = Flask(__name__)

    @app.route('/df_to_csv', methods=['POST'])
    def index():
        return df_to_csv(request)

    app.run('0.0.0.0', 5000, debug=True)

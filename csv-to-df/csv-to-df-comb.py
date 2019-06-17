#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import json
import time
import os
import re
import json
from pprint import pprint as pp


# In[2]:


import sys
myargs = sys.argv
if '-f' in myargs:
    try: FILE_NAME = myargs[2]
    except Exception as e:
        print(e)
        FILE_NAME = 'template'
else:
    FILE_NAME = 'template'
    os.system("cp ./template.csv ./temp/")
# if testing on jupyter notebook
if FILE_NAME[0] == "/":
    FILE_NAME = 'template'
    os.system("cp ./template.csv ./temp/")

# generate ID
import random
def generate_ID():
    c = ["".join([random.choice('01234567890abcdef') for _ in range(4)]) 
         for _ in range(8)]
    return c[0]+c[1]+"-"+c[2]+"-"+c[3]+"-"+c[4]+"-"+c[5]+c[6]+c[7]

generate_ID()


# In[30]:


# copy template
os.system("rm -r temp/{}".format(FILE_NAME))
os.system("cp -r stencil temp/{}".format(FILE_NAME))
os.system("mkdir temp/{}/entities".format(FILE_NAME))


# # Converting intents

# In[31]:


df = pd.read_csv('temp/{}.csv'.format(FILE_NAME), header=0)
df


# In[32]:


# get column number for manipulation next
col_num_INTENT_NAME = df.columns.get_loc("INTENT_NAME")
col_num_IN = df.columns.get_loc("INPUT_CONTEXT")
col_num_OUT = df.columns.get_loc("OUTPUT_CONTEXT")
col_num_USER = df.columns.get_loc("USER_SAYS")
cols_name_RESP = [col for col in df if col.startswith('RESPONSES')]
cols_num_RESP = []
for col_name_RESP in cols_name_RESP:
    cols_num_RESP.append(df.columns.get_loc(col_name_RESP))
cols_num_RESP.append(len(df.columns))
col_num_total = len(df.columns)


# In[33]:


def rm_nan(list_of_list):
    '''remove nan from list of list'''
    return [[x for x in list_ if x == x] for list_ in list_of_list]
    
df['INPUT_CONTEXT_L'] = rm_nan(df.iloc[:,col_num_IN:col_num_OUT].values.tolist())
df['OUTPUT_CONTEXT_L'] = rm_nan(df.iloc[:,col_num_OUT:col_num_USER].values.tolist())
df['USER_SAYS_L'] = rm_nan(df.iloc[:,col_num_USER:cols_num_RESP[0]].values.tolist())
for i,col_num_RESP in enumerate(cols_num_RESP[:-1]):
    df['RESPONSES_L_{}'.format(i)] = rm_nan(df.iloc[:,col_num_RESP:cols_num_RESP[i+1]].values.tolist())


# In[34]:


# combine columns, ignoring nan
# https://stackoverflow.com/questions/45787782/combine-multiple-columns-in-pandas-excluding-nans
# df['INPUT_CONTEXT_L'] = df.iloc[:,col_num_IN:col_num_OUT].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# df['OUTPUT_CONTEXT_L'] = df.iloc[:,col_num_OUT:col_num_USER].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# df['USER_SAYS_L'] = df.iloc[:,col_num_USER:col_num_RESP].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# df['RESPONSES_L'] = df.iloc[:,col_num_RESP:col_num_total].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# I don't understand why line 1 works but line 3 and 4 don't work. WTF.


# In[35]:


df


# In[36]:


# # for line in rows of excel
# intent_df_row = None 
for index, row in df.iterrows():  # CURRENTLY ONLY PROCESSING ONE ROW
#     if index == 4:
    intent_df_row = row
#     break


# In[37]:


    intent_name = intent_df_row['INTENT_NAME']
    input_contexts = intent_df_row['INPUT_CONTEXT_L']
    output_contexts = [[y.strip() for y in x.split(',')]
                       for x in intent_df_row['OUTPUT_CONTEXT_L']]
    training_phrases = intent_df_row['USER_SAYS_L']
    responses = [intent_df_row['RESPONSES_L_{}'.format(i)] for i,x in enumerate(cols_num_RESP[:-1])]
    responses = [x for x in responses if x != []]


    # In[38]:


    # define a list/dictionary for {intent_name}.json
    intent_jsonfile = {}
    intent_jsonfile["id"] = generate_ID() # to randomly generate
    intent_jsonfile["name"] = intent_name
    intent_jsonfile["auto"] = True # will change to lowercase when converted to jsonfile
    intent_jsonfile["contexts"] = input_contexts

    intent_jsonfile_responses = {}
    intent_jsonfile_responses["resetContexts"] = False
    intent_jsonfile_responses["affectedContexts"] = []

    for output_context in output_contexts:
        affectedContext = {}
        affectedContext["name"] = output_context[1]
        affectedContext["parameters"] = {}
        affectedContext["lifespan"] = output_context[0]
        intent_jsonfile_responses["affectedContexts"].append(affectedContext)

    intent_jsonfile_responses["parameters"] = []
    intent_jsonfile_responses["messages"] = []  # probably allow for list of messages? yes



    for response_bubble in responses:
        try:
            json_object = json.loads(response_bubble[0])
            if type(json_object) == dict:
                message = {}
                message["type"] = 4
                message["lang"] = "en"
                message["payload"] = json_object
                intent_jsonfile_responses["messages"].append(message)
                continue

        except:
            pass

        message = {}
        message["type"] = 0
        message["lang"] = "en"
        message["speech"] = response_bubble
        intent_jsonfile_responses["messages"].append(message)

    intent_jsonfile_responses["defaultResponsePlatforms"] = []
    intent_jsonfile_responses["speech"] = []
    intent_jsonfile["responses"] = [intent_jsonfile_responses]  #

    intent_jsonfile["priority"] = 500000
    intent_jsonfile["webhookUsed"] = False
    intent_jsonfile["webhookForSlotFilling"] = False
    intent_jsonfile["lastUpdate"] = int(time.time())
    intent_jsonfile["fallbackIntent"] =  False
    intent_jsonfile["events"] = []

    # 'messages': [{'speech': '<3', 'lang': 'en', 'type': 0}, 
    #              {'speech': 'this is a second response bubble', 'lang': 'en', 'type': 0}, 
    #              {'payload': {'trap': 'trying to break this system'}, 'lang': 'en', 'type': 4}]


    # In[39]:


    print(json.dumps(intent_jsonfile))


    # {
    #   "id": "f60c8a1f-2911-448b-90c6-facd27259ed0",
    #   "name": "training phrases test",
    #   "auto": true,
    #   "contexts": [
    #     "inputcontexttest"
    #   ],
    #   "responses": [
    #     {
    #       "resetContexts": false,
    #       "affectedContexts": [
    #         {
    #           "name": "outputcontexttest",
    #           "parameters": {},
    #           "lifespan": 999
    #         }
    #       ],
    #       "parameters": [],
    #       "messages": [
    #         {
    #           "type": 0,
    #           "lang": "en",
    #           "speech": [
    #             "sample response one",
    #             "sample response two",
    #             "sample response three"
    #           ]
    #         }
    #       ],
    #       "defaultResponsePlatforms": {},
    #       "speech": []
    #     }
    #   ],
    #   "priority": 500000,
    #   "webhookUsed": false,
    #   "webhookForSlotFilling": false,
    #   "lastUpdate": 1548814094,
    #   "fallbackIntent": false,
    #   "events": []
    # }

    # In[40]:


    # define a list/dictionary for {intent_usersays_name}.json
    intent_usersays_jsonfile = []
    for training_phrase in training_phrases:
        user_say = {}
        user_say["id"] = generate_ID()
        user_say["data"] = []  # no entities for now and the near future
        snippet = {}
        snippet["text"] = training_phrase
        snippet["userDefined"] = False
        user_say["data"] = [snippet]

        user_say["isTemplate"] = False
        user_say["count"] = 0
        user_say["updated"] = int(time.time())
        intent_usersays_jsonfile.append(user_say)


    # In[41]:


    print(json.dumps(intent_usersays_jsonfile))


    # [
    #   {
    #     "id": "f65bbd35-97d6-4862-bd56-5e360dbe7d08",
    #     "data": [
    #       {
    #         "text": "training phrase ",
    #         "userDefined": false
    #       },
    #       {
    #         "text": "three",
    #         "meta": "@sys.ignore",
    #         "userDefined": false
    #       }
    #     ],
    #     "isTemplate": false,
    #     "count": 0,
    #     "updated": 1548814041
    #   }
    # ]

    # In[42]:
        
    intent_name = re.sub(r"[^a-zA-Z0-9- ]", '_', intent_name)
    filepath_prefix = 'temp/{}/intents/{}'.format(FILE_NAME, intent_name)
    counter_file = 0
    
    
    if intent_name == "Default Welcome Intent":
        intent_jsonfile["events"] = [{"name": "WELCOME"}]
    elif intent_name == "Default Fallback Intent":
        intent_jsonfile["fallbackIntent"] = True
        intent_jsonfile["responses"][0]["action"] = "input.unknown"
    else:
        # intent_name in the .json files are different
        # however, we have to prevent collision after the replacement
        while os.path.isfile("{}.json".format(filepath_prefix)):
            counter_file += 1
            filepath_prefix += str(counter_file)
    
    with open("{}.json".format(filepath_prefix), 'w', encoding='utf-8') as outfile:
        json.dump(intent_jsonfile, outfile, ensure_ascii=False)
    
    with open('{}_usersays_en.json'.format(filepath_prefix), 'w', encoding='utf-8') as outfile:
        json.dump(intent_usersays_jsonfile, outfile, ensure_ascii=False)        
        
# then process the next intent


# In[43]:


# "project": "newagent-fcefe" may be an issue
agent_json = '''{
  "description": "",
  "language": "en",
  "disableInteractionLogs": false,
  "disableStackdriverLogs": true,
  "googleAssistant": {
    "googleAssistantCompatible": false,
    "project": "newagent-fcefe",
    "welcomeIntentSignInRequired": false,
    "startIntents": [],
    "systemIntents": [],
    "endIntentIds": [],
    "oAuthLinking": {
      "required": false,
      "grantType": "AUTH_CODE_GRANT"
    },
    "voiceType": "MALE_1",
    "capabilities": [],
    "protocolVersion": "V2",
    "isDeviceAgent": false
  },
  "defaultTimezone": "Asia/Hong_Kong",
  "webhook": {
    "available": false,
    "useForDomains": false,
    "cloudFunctionsEnabled": false,
    "cloudFunctionsInitialized": false
  },
  "isPrivate": true,
  "customClassifierMode": "use.after",
  "mlMinConfidence": 0.3,
  "supportedLanguages": [],
  "onePlatformApiVersion": "v2",
  "analyzeQueryTextSentiment": false,
  "enabledKnowledgeBaseNames": [],
  "knowledgeServiceConfidenceAdjustment": -0.4,
  "dialogBuilderMode": false
}'''


# # Converting entities

# In[44]:


df = pd.read_csv('temp/{}.csv'.format(FILE_NAME + "-ent"), header=0)
df


# In[45]:


# get column number for manipulation next
col_num_ENTITY_NAME = df.columns.get_loc("ENTITY_NAME")
col_num_ENTITY_VALUE = df.columns.get_loc("ENTITY_VALUE")
col_num_SYNONYMS = df.columns.get_loc("SYNONYMS")


# In[46]:


def rm_nan_sym(list_of_list):
    '''remove nan from list of list'''
    return [[x for x in list_ if x == x] for list_ in list_of_list][0]


# In[47]:


# # for line in rows of excel
# intent_df_row = None 
entities = []
entity = {}
entity_name = "Error: please enter entity name for the first entity"
for index, row in df.iterrows():  # CURRENTLY ONLY PROCESSING ONE ROW
#     if index == 4:
    intent_df_row = row

    synomyms = rm_nan_sym([intent_df_row[col_num_SYNONYMS:]])
    if type(intent_df_row['ENTITY_NAME']) == str:
        entities.append(entity)
        entity = {}
        entity_name = intent_df_row['ENTITY_NAME']
        entity["ENTITY_NAME"] = entity_name
        entity["ENTRIES"] = [{intent_df_row['ENTITY_VALUE'] : synomyms}]
    else:
        entity["ENTRIES"].append({intent_df_row['ENTITY_VALUE'] : synomyms})
entities.append(entity)
entities = entities[1:]


# In[48]:

try:
    pp(entities)
except:
    pass

# In[49]:


# {'allowFuzzyExtraction': False,
#  'automatedExpansion': False,
#  'id': '7d52d2e6-a1ae-45f2-b53f-3d07fdbc4ec0',
#  'isEnum': False,
#  'isOverridable': True,
#  'isRegexp': False,
#  'name': 'Amount'}

# [{'synonyms': ['180'], 'value': '180'},
#  {'synonyms': ['@Amoun'], 'value': '@Amount'}]


# In[50]:


# define a list/dictionary for {intent_name}.json
for entity in entities:
    entity_jsonfile = {}
    entity_jsonfile["id"] = generate_ID() # to randomly generate
    entity_jsonfile["name"] = entity["ENTITY_NAME"]
    entity_jsonfile["automatedExpansion"] = False  # will change to lowercase when converted to jsonfile
    entity_jsonfile["allowFuzzyExtraction"] = False
    entity_jsonfile["isEnum"] = False
    entity_jsonfile["isOverridable"] = True
    entity_jsonfile["isRegexp"] = False

    synonyms_jsonfile = []
    for entry in entity['ENTRIES']:
        entity_entry = {}
        for key, value in entry.items():
            entity_entry['value'] = key
            entity_entry['synonyms'] = value
        synonyms_jsonfile.append(entity_entry)
        
    with open('temp/{}/entities/{}.json'.format(FILE_NAME, entity["ENTITY_NAME"]), 'w') as outfile:
        json.dump(entity_jsonfile, outfile)

    with open('temp/{}/entities/{}_entries_en.json'.format(FILE_NAME, entity["ENTITY_NAME"]), 'w') as outfile:
        json.dump(synonyms_jsonfile, outfile)


# # Zipping folder

# In[51]:


os.system("rm template.zip")
os.system("cd temp/{}/ && zip -r ../{}.zip * -x *.DS_Store".format(FILE_NAME, FILE_NAME))


# In[52]:


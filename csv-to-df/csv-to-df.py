#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import json
import time
import os
import re


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


# generate ID
import random

def generate_ID():
    c = ["".join([random.choice('01234567890abcdef') for _ in range(4)]) 
         for _ in range(8)]
    return c[0]+c[1]+"-"+c[2]+"-"+c[3]+"-"+c[4]+"-"+c[5]+c[6]+c[7]

generate_ID()


# In[ ]:


# copy template
# os.system("rm -r template")
os.system("cp -r stencil temp/{}".format(FILE_NAME))


# In[3]:


df = pd.read_csv('temp/{}.csv'.format(FILE_NAME), header=0)
df


# In[4]:


# get column number for manipulation next
col_num_INTENT_NAME = df.columns.get_loc("INTENT_NAME")
col_num_IN = df.columns.get_loc("INPUT_CONTEXT")
col_num_OUT = df.columns.get_loc("OUTPUT_CONTEXT")
col_num_USER = df.columns.get_loc("USER_SAYS")
col_num_RESP = df.columns.get_loc("RESPONSES")
col_num_total = len(df.columns)


# In[ ]:


print(col_num_INTENT_NAME,col_num_IN,col_num_OUT,col_num_USER,col_num_RESP,col_num_total)


# In[ ]:


df.iloc[:,col_num_USER:col_num_RESP].values.tolist()


# In[15]:


df.iloc[:,col_num_IN:col_num_OUT].values.tolist()


# In[23]:


def rm_nan(list_of_list):
    '''remove nan from list of list'''
    return [[x for x in list_ if x == x] for list_ in list_of_list]
    
df['INPUT_CONTEXT_L'] = rm_nan(df.iloc[:,col_num_IN:col_num_OUT].values.tolist())
df['USER_SAYS_L'] = rm_nan(df.iloc[:,col_num_USER:col_num_RESP].values.tolist())
df['RESPONSES_L'] = rm_nan(df.iloc[:,col_num_RESP:col_num_total].values.tolist())


# In[24]:


# combine columns, ignoring nan
# https://stackoverflow.com/questions/45787782/combine-multiple-columns-in-pandas-excluding-nans
# df['INPUT_CONTEXT_L'] = df.iloc[:,col_num_IN:col_num_OUT].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# df['USER_SAYS_L'] = df.iloc[:,col_num_USER:col_num_RESP].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# df['RESPONSES_L'] = df.iloc[:,col_num_RESP:col_num_total].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
df['OUTPUT_CONTEXT_L'] = df.iloc[:,col_num_OUT:col_num_USER].apply(lambda x: list(x.dropna()), axis=1).values.tolist()
# I don't understand why line 1 works but line 3 and 4 don't work. WTF.


# In[25]:


df


# In[26]:


df['OUTPUT_CONTEXT_L']


# In[27]:


# # for line in rows of excel
# intent_df_row = None 
for index, row in df.iterrows():  # CURRENTLY ONLY PROCESSING ONE ROW
    intent_df_row = row
    #     break


    # In[28]:


    intent_name = intent_df_row['INTENT_NAME']
    input_contexts = intent_df_row['INPUT_CONTEXT_L']
    output_contexts = [[y.strip() for y in x.split(',')]
                       for x in intent_df_row['OUTPUT_CONTEXT_L']]
    training_phrases = intent_df_row['USER_SAYS_L']
    responses = intent_df_row['RESPONSES_L']


    # In[29]:


    print(output_contexts)  # I don't know why does this work


    # In[30]:


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
    intent_jsonfile_responses["messages"] = []  # probably allow for list of messages?
    message = {}
    message["type"] = 0
    message["lang"] = "en"
    message["speech"] = responses
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


    # In[31]:


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

    # In[32]:


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


    # In[33]:


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

    # In[34]:
    intent_name = re.sub(r"[^a-zA-Z0-9- ]", '_', intent_name)

    with open('temp/{}/intents/{}.json'.format(FILE_NAME, intent_name), 'w') as outfile:
        json.dump(intent_jsonfile, outfile)

    with open('temp/{}/intents/{}_usersays_en.json'.format(FILE_NAME, intent_name), 'w') as outfile:
        json.dump(intent_usersays_jsonfile, outfile)

    # then process the next intent


# In[35]:


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


# In[36]:


# os.system("rm template.zip")
os.system("cd temp/{}/ && zip -r ../{}.zip * -x *.DS_Store".format(FILE_NAME, FILE_NAME))


# In[37]:


# get_ipython().system('jupyter nbconvert --to script *.ipynb')


# In[ ]:

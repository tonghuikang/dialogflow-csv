#!/usr/bin/env python
# coding: utf-8

# In[2]:


import glob
import json
import pandas as pd
import numpy as np
import os
from pprint import pprint as pp


# In[ ]:

import sys
myargs = sys.argv
if '-f' in myargs:
    try: FILE_NAME = myargs[2]
    except Exception as e:
        print(e)
        FILE_NAME = 'template'
else:
    FILE_NAME = 'template'


os.system("rm -rf ./template")
os.system("unzip {}.zip -d {}".format(FILE_NAME, FILE_NAME))
os.system("tree")


# In[ ]:


files = sorted([intent for intent in glob.glob('{}/intents/*.json'.format(FILE_NAME, FILE_NAME))])
# files.remove('template/intents/Default Fallback Intent.json')
# files.remove('template/intents/consideration-no_usersays_en.json')


# In[ ]:


# does not assume that all intents have usersays
# assume English only
intent_hold = "none" 
intent_jsons = []
for file in files:
    intent_name = file.rpartition('.')[0]
    if not intent_name.startswith(intent_hold):
        intent_jsons.append([file])
        intent_hold = intent_name
    else:
        intent_jsons[-1].append(file)


# In[ ]:


intents = []
for intent_json in intent_jsons:
    try:
        intent = {}
        intent_info_json = intent_json[0]
        usersays_jsons = intent_json[1:] # should be one only

        with open(intent_info_json, encoding="utf-8") as f:
            intent_info = json.load(f)
        intent["INTENT_NAME"] = intent_info["name"]
        intent["INPUT_CONTEXT"] = intent_info["contexts"]
        intent["OUTPUT_CONTEXT"] = [str(c["lifespan"]) + ", " + str(c["name"])  
                                    for c in intent_info["responses"][0]["affectedContexts"]]

        response_list_or_str = intent_info["responses"][0]["messages"][0]["speech"]
        if type(response_list_or_str) == str:
            intent["RESPONSES"] = [response_list_or_str]
        else: 
            intent["RESPONSES"] = [m for m in response_list_or_str]

        intent["USER_SAYS"] = []
        for usersays_json in usersays_jsons: # should be one or none
            with open(usersays_json) as f:
                usersays_info = json.load(f)
            for usersay in usersays_info:
                intent["USER_SAYS"].append(usersay["data"][0]["text"])
        intents.append(intent)
    #     pp(intent_info)
    #     break
    except:
        pass


# In[ ]:


intents


# In[ ]:


len_INPUT_CONTEXT = max([len(intent["INPUT_CONTEXT"]) for intent in intents]+[1])
len_OUTPUT_CONTEXT = max([len(intent["OUTPUT_CONTEXT"]) for intent in intents]+[1])
len_USER_SAYS = max([len(intent["USER_SAYS"]) for intent in intents]+[1])
len_RESPONSES = max([len(intent["RESPONSES"]) for intent in intents]+[1])
lengths = [1, len_INPUT_CONTEXT, len_INPUT_CONTEXT, len_USER_SAYS, len_RESPONSES]


# In[ ]:


row_length = sum(lengths)
columns = [""]*row_length
columns[0] = "INTENT_NAME"
columns[sum(lengths[:1])] = "INPUT_CONTEXT"
columns[sum(lengths[:2])] = "OUTPUT_CONTEXT"
columns[sum(lengths[:3])] = "USER_SAYS"
columns[sum(lengths[:4])] = "RESPONSES"


# In[ ]:


row_list = []
for intent in intents:
    row = [np.nan]*row_length
    row[0] = intent["INTENT_NAME"]
    row[sum(lengths[:1]):sum(lengths[:1])+len(intent["INPUT_CONTEXT"])] = intent["INPUT_CONTEXT"]
    row[sum(lengths[:2]):sum(lengths[:2])+len(intent["OUTPUT_CONTEXT"])] = intent["OUTPUT_CONTEXT"]
    row[sum(lengths[:3]):sum(lengths[:3])+len(intent["USER_SAYS"])] = intent["USER_SAYS"]
    row[sum(lengths[:4]):sum(lengths[:4])+len(intent["RESPONSES"])] = intent["RESPONSES"]
    row_list.append(row)


# In[ ]:


df = pd.DataFrame(row_list, columns=columns)
df


# In[ ]:


df.to_csv("{}.csv".format(FILE_NAME))


# In[31]:


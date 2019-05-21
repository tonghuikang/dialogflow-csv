#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import json
import pandas as pd
import numpy as np
import os
from pprint import pprint as pp


# In[2]:


# loading testing template
import sys
myargs = sys.argv
if '-f' in myargs:
    try: FILE_NAME = myargs[2]
    except Exception as e:
        print(e)
        FILE_NAME = 'template'
else:
    os.system("cp ./template.zip ./temp/")
    FILE_NAME = 'template'
# if testing on jupyter notebook
if FILE_NAME[0] == "/":
    os.system("cp ./template.zip ./temp/")
    FILE_NAME = 'template'


# In[3]:


os.system("rm -rf ./temp/template")
os.system("unzip temp/{}.zip -d temp/{}".format(FILE_NAME, FILE_NAME))
os.system("tree")


# In[4]:


files = sorted([intent for intent in glob.glob('temp/{}/intents/*.json'.format(FILE_NAME, FILE_NAME))])
# files.remove('template/intents/Default Fallback Intent.json')
# files.remove('template/intents/consideration-no_usersays_en.json')


# In[5]:


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


# In[6]:


intents = []
for intent_json in intent_jsons:
#     try:
        intent = {}
        intent_info_json = intent_json[0]
        usersays_jsons = intent_json[1:] # should be one only

        with open(intent_info_json, encoding="utf-8") as f:
            intent_info = json.load(f)
        
        intent["INTENT_NAME"] = intent_info["name"]
        intent["INPUT_CONTEXT"] = intent_info["contexts"]
        intent["OUTPUT_CONTEXT"] = [str(c["lifespan"]) + ", " + str(c["name"])  
                                    for c in intent_info["responses"][0]["affectedContexts"]]
        intent["RESPONSES"] = []
        
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
                intent["USER_SAYS"].append(usersay["data"][0]["text"])
        intents.append(intent)
    #     pp(intent_info)
    #     break
#     except:
        pass


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
lengths = [1, len_INPUT_CONTEXT, len_OUTPUT_CONTEXT, len_USER_SAYS, *lens_RESPONSES]


# In[10]:


row_length = sum(lengths)
columns = [""]*row_length
columns[0] = "INTENT_NAME"
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


df.to_csv("temp/{}.csv".format(FILE_NAME))


# In[14]:


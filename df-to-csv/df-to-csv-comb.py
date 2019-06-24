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

# def print(*args):
#     pass

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
os.system("echo {}".format(FILE_NAME))


# In[4]:

import random
def generate_ID():
    c = ["".join([random.choice('01234567890abcdef') for _ in range(4)]) 
         for _ in range(8)]
    return c[0]+c[1]+"-"+c[2]+"-"+c[3]+"-"+c[4]+"-"+c[5]+c[6]+c[7]
rand_string = generate_ID()

def rreplace(s, old, new, count=1):
     return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]

# please test this code
# - "_usersays" multiple times
# - "!!!" multiple times
files = glob.glob('temp/{}/intents/*.json'.format(FILE_NAME, FILE_NAME))
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
                # print([usersay_chunk["text"] for usersay_chunk in usersay["data"]])  # cannot print \u0027
                intent["USER_SAYS"].append("".join([usersay_chunk["text"] for usersay_chunk in usersay["data"]]))
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


# In[6]:

# please test this code
# - "_entries" multiple times
# - "!!!" multiple times
files = glob.glob('temp/{}/entities/*.json'.format(FILE_NAME, FILE_NAME))
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


entities = []
for entity_json in entity_jsons:
#     try:
        print(entity_json)
        entity = {}
        entity_info_json = entity_json[0]
        usersays_jsons = entity_json[1:] # should be one only

        with open(entity_info_json, encoding="utf-8") as f:
            entity_info = json.load(f)

        entity["ENTITY_NAME"] = entity_info["name"]
        entity["ENTRIES"] = []
        
        for usersays_json in usersays_jsons: # should be one or none
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
    for entries in entity["ENTRIES"]:
        row = [entity_name]
        for key, value in entries.items():
            row += [key]
            row += value
            entity_name = ""
            break
        row_list.append(row)


# In[11]:


max_len = max([3] + [len(row) for row in row_list])

columns = ["ENTITY_NAME", "ENTITY_VALUE", "SYNONYMS"] + [""]*(max_len-3)
for i,row in enumerate(row_list):
    row_list[i] = row + [""]*(max_len-len(row))


# In[12]:


df = pd.DataFrame(row_list, columns=columns)
df


# In[13]:


df.to_csv("temp/{}-ent.csv".format(FILE_NAME))

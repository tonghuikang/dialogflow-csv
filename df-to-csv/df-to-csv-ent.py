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


FILE_NAME = 'SPH'


# In[4]:


os.system("rm -rf ./temp/template")
os.system("rm -rf ./temp/{}".format(FILE_NAME))
os.system("unzip temp/{}.zip -d temp/{}".format(FILE_NAME, FILE_NAME))
os.system("tree")


# In[5]:


get_ipython().system('tree')


# In[6]:


files = sorted([entity for entity in glob.glob('temp/{}/entities/*.json'.format(FILE_NAME, FILE_NAME))])
files


# In[7]:


# assume English only
entity_hold = "none"
entity_jsons = []
for file in files:
    entity_name = file.rpartition('.')[0]
    if not entity_name.startswith(entity_hold):
        entity_jsons.append([file])
        entity_hold = entity_name
    else:
        entity_jsons[-1].append(file)
entity_jsons


# In[8]:


entities = []
for entity_json in entity_jsons:
#     try:
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


# In[14]:


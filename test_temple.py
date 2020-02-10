import json
import os

with open('./layout1.json','r',encoding='utf-8') as json_file: 
    data=json.load(json_file)
    pre_matrix = data['pre']
    dis_matrix = data['dis']

data = {"pre":pre_matrix, "dis":dis_matrix, "m":6, "n":6}
with open("./layout0.json",'w',encoding='utf-8') as json_file:
    json.dump(data,json_file,ensure_ascii=False)
    
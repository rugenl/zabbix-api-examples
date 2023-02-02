from pyzabbix import ZabbixAPI
from os import environ
import re

def split_key(key):
    i = key.index("[")
    key = key[i+1:-1]
    lst = key.split(",")
    return lst

def replace_with_list_index(text, lst):
    result = ''
    while "$" in text:
        i = text.index("$")
        j = i + 1
        num = ''
        while j < len(text) and text[j].isdigit():
            num += text[j]
            j += 1
        num = int(num)
        result += text[:i]
        result += lst[num-1]
        text = text[j:]
    result += text
    return result

# activate these lines for tracing
#import logging
#logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+environ['host']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)

# Login to the Zabbix API

zapi.login(environ['user'], environ['pass'])

print("$ in templates")
items = zapi.item.get(templated='true',output='extend')

for item in items:
   if re.search('\$[1-9]',item["name"]):
      host = zapi.template.get(templateids=item["hostid"],output=["templateid", "name"])
      if len(host) == 0:
         print(item["hostid"], "template.get failed")
      else:
         print(host[0]["name"],item["name"], item["key_"])
         list_key = split_key(item["key_"])
         newitemname = replace_with_list_index(item["name"],list_key)
         zapi.item.update(itemid=item["itemid"],name=newitemname)
 
print()
print("$ in item prototypes")
items = zapi.itemprototype.get(templated="true",output='extend')

for item in items:
   if re.search('\$[1-9]',item["name"]):
      host = zapi.template.get(templateids=item["hostid"])
      if len(host) == 0:
          print(item["hostid"], "host.get failed")
      else:
          print("host = ", host[0]["name"],", itemname = ", item["name"],", key = ", item["key_"])
          list_key = split_key(item["key_"])
          newitemname = replace_with_list_index(item["name"], list_key)
          zapi.itemprototype.update(itemid=item["itemid"],name=newitemname)

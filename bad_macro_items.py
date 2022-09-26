"""
Get hosts in passed group    
"""

from pyzabbix import ZabbixAPI
from os import environ
import re

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
 
print()
print("$ in item prototypes")
items = zapi.itemprototype.get(templated="true",output='extend')

for item in items:
   if re.search('\$[1-9]',item["name"]):
      host = zapi.template.get(templateids=item["hostid"])
      if len(host) == 0:
          print(item["hostid"], "host.get failed")
      else:
          print(host[0]["name"],item["name"])
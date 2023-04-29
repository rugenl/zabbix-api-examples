#!/usr/bin/python3
"""
Get a host usermacro value

Parameters:
    1) host name
    2) macro name

Returns only type 0 macros

Uses https://github.com/lukecyca/pyzabbix
"""

from pyzabbix import ZabbixAPI

import sys
from os import environ
import pprint

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#import logging 
#logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+environ['Zhost']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.session.verify = False

# Login to the Zabbix API
zapi.login(environ['Zuser'], environ['Zpass'])

host_name = str(sys.argv[1])
macro_name = str(sys.argv[2])

macros = zapi.usermacro.get(output='extend',
        filter={"host": host_name})

#pprint.pprint(macros)

for m in macros:
    if m["macro"] == macro_name and m["type"] == "0":
        print(m["value"])
        exit(0)

print("!Invalid macro")
exit(8)

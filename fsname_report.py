#!/usr/bin/python3
#
# Generate summary of filesystem names in DEVOP systems
#

from pyzabbix import ZabbixAPI
from operator import itemgetter
import sys
from os import environ

#import logging 
#logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+environ['Zhost']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)

sel_groups = ["DEVOP/Linux*", "DEVOP/Windows*"]
    
# Login to the Zabbix API
zapi.login(environ['Zuser'], environ['Zpass'])

group_hosts = zapi.hostgroup.get(output='extend',search={'name':sel_groups},searchByAny="true",searchWildcardsEnabled="true",selectHosts=['name'])
exclude = ['/', '/boot', 'C:', '/tmp']

for group in sorted(group_hosts, key=itemgetter('name')):
   for host in sorted(group['hosts'], key=itemgetter('name')):
      host_items = zapi.host.get(output='extend',hostids=host['hostid'],selectItems=['key_'])
      for item in host_items[0]['items']:
         if item['key_'].find('vfs.fs.size') > -1 and item['key_'].find('total') > -1:
            fsname_temp = item['key_'].replace('vfs.fs.size[','')
            fsname = fsname_temp.replace(',total]','')
            if fsname not in exclude:
               print(group['name']+','+host['name']+','+fsname)

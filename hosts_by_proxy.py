#!/usr/bin/python3
"""
Get selected host group starting with CSG, UM DOIT and User monitor. 
"""

from pyzabbix import ZabbixAPI

import json
from os import environ

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+environ['Zhost']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)

# Login to the Zabbix API
zapi.login(environ['Zuser'], environ['Zpass'])

print("<html>")
print("<title>Zabbix Hosts by Proxy</title>")
print("<body>")
print("<h1>Zabbix Hosts by Proxy</h1>")

proxies = zapi.proxy.get(output='extend',sortfield='host')

#print json.dumps(proxies, indent=4, sort_keys=True)

for proxy in proxies:
    proxy_id = proxy['proxyid']
    proxy_name = proxy['host'] 
    count = 0
    items = 0

    print("<h3>"+proxy_name+"</h3>")
    hosts =  zapi.host.get(output=['host'], proxyids=proxy_id, sortfield='host',selectItems='count')
    print("<ol>")
    for host in hosts:
       print("<li>"+host['host'], 'items', host['items'], '</li>')
       count += 1
       items += int(host['items'])
    
    print("</ol>")
    print("<p>Monitored hosts:", count, 'with', items, 'items') 

print("<h3>zabbix5-server.doit.missouri.edu</h3>")

count = 0
items = 0
hosts =  zapi.host.get(output=['host', 'proxy_hostid'], sortfield='host', selectItems='count')
print("<ol>")
for host in hosts:
#    print host['host']
    if host['proxy_hostid'] == '0':
#      print json.dumps(host, indent=4, sort_keys=True)
       print("<li>"+host['host'], "items", host['items'], "</li>")
       count += 1
       items += int(host['items'])

print("</ol>")
print("<p>Monitored hosts:", count, 'with', items, 'items') 

print("</body>")
print("</html")

# print json.dumps(members, indent=4, sort_keys=True)

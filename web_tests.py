#!/usr/bin/python3  

from pyzabbix import ZabbixAPI
from os import environ
import pprint
from datetime import *
from operator import itemgetter

#import logging 
#logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)
	
# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+environ['Zhost']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)

# Login to the Zabbix API
zapi.login(environ['Zuser'], environ['Zpass'])

web_tests = zapi.httptest.get(output="extend", monitored="true", 
            expandName="true", selectTags="extend", expandStepName="true", 
            selectSteps="extend", sortfield=["name"])

print("<html>")
print("<title>Zabbix web tests</title>")
print("<body>")
print("<h1>Zabbix web tests</h1>")
print("<p style=\"background-color:tomato;\">HTTPS Tests with Unverified SSL Components</p>")
print("<table>")
print("<tr><th>Host</th><th>Web Test</th><th>First URL</th><th>Verify<br>Peer</th><th>Verify<br>Host</th><th>Tag</th></tr>")

# Create Contents
lag_hostid = ""
for test in sorted(web_tests, key=itemgetter('hostid')):
   if lag_hostid != test['hostid']:
       host = zapi.host.get(output="extend", hostids=test['hostid'])
       lag_hostid = test['hostid']
   test['host'] = host[0]['name']
   
for test in sorted(web_tests, key=itemgetter('host')):
   if len(test["tags"]) > 0:
       for tag in test["tags"]:
          if "ZBX_Vhost" in tag["tag"]:
             tag = tag["tag"] + ":" + tag["value"]
             break
          else:
             tag = ""
   if (test['verify_peer'] == '0' or test['verify_host'] == '0') and "https:" in test['steps'][0]['url']:
       print("<tr style=\"background-color:tomato;\"><td>"+test['host']+"</td><td>"+test['name']+ \
             "</td><td>"+test['steps'][0]['url']+"</td><td>"+test['verify_peer']+"</td><td>"+ \
              test['verify_host']+"</td><td>"+ tag + "</td></tr>")
   else:
       print("<tr><td>"+test['host']+"</td><td>"+test['name']+ \
             "</td><td>"+test['steps'][0]['url']+"</td><td>"+test['verify_peer']+"</td><td>"+ \
              test['verify_host']+"</td><td>"+ tag + "</td></tr>")


print("</table></br>")

print("<h2>Total web tests found", str(len(web_tests))+"</h2>")

print("</body>")
print("</html>")

#!/usr/bin/python3  
"""
Get alerts. 
"""

from pyzabbix import ZabbixAPI

from  datetime import *

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF8')

#import logging 
#logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)

import sys
from os import environ

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+environ['Zhost']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)
  
# Login to the Zabbix API
zapi.login(environ['Zuser'], environ['Zpass'])

today_8am = datetime.combine(date.today(), time(8))
yesterday_8am = today_8am - timedelta(days=30)

end = today_8am.strftime("%s")
st = yesterday_8am.strftime("%s")

medias = zapi.mediatype.get()

network_alerts = 0

print("<html>")
print("<title>Zabbix remote commands sent from", yesterday_8am.strftime("%c"), "to", today_8am.strftime("%c"), "</title>")
print("<body>")
print("<p>Zabbix remote commands sent from", yesterday_8am.strftime("%c"), "to", today_8am.strftime("%c"), "</p>")
print("<table border=\"2\">")
print("<tr><th>Date - Time</th><th>Ack</th><th>User Name</th><th>MediaType</th><th>SendTo</th><th>Status</th><th>Subject - Command</th></tr>")

users = zapi.user.get(output="extend")

alerts = zapi.alert.get(time_from=st, time_till=end, filter={"alerttype": "1"}, output="extend")

for alert in alerts:
    clock = alert["clock"]
    event_id = alert["eventid"]
    subject = alert["subject"] 
    sendto = alert["sendto"] 
    alerttype = alert["alerttype"]
    alertmediatypeid = alert["mediatypeid"]
    alertretries = alert["retries"]
    alerterror = alert["error"]
    status = alert["status"]
    message = alert["message"]
    alert_userid = alert['userid']
    messageTime = datetime.fromtimestamp(int(clock)).strftime('%Y-%m-%d %H:%M:%S') 

    if alerttype == "0":
       try:
           mediatype = next((item for item in medias if item["mediatypeid"] == alertmediatypeid))
           mediadescription = mediatype["description"]
       except StopIteration:
           mediadescription = "** No Media **"
    else:
       mediadescription = " "

    if status == "0":
       alertstatus_txt = "Not sent"
    elif status == "1":
       alertstatus_txt = ""
    elif status == "2":
       alertstatus_txt = "Failed"
    else:
       alertstatus_txt = "Unknown"

    if sendto == 'EventTranslator':
        network_alerts = network_alerts + 1
    elif alerttype == '1':
        print("<tr><td>", messageTime, "</td><td></td></td><td>REMOTE COMMAND</td><td colspan=4>", message, "</td></tr>")
        if status != "1":
            print("<tr><td></td><td></td><td>Error</td><td colspan=4>", alerterror, "</td></tr>")
    else:
        user = next((item for item in users if item["userid"] == alert_userid))
        user_alias = user['username']
        user_name = user['name']
        user_surname = user['surname']
        user_fullname = user_name+" "+user_surname
        event = zapi.event.get(select_acknowledges="extend",eventids=event_id,limit=25) 
        acknowledged = event[0]["acknowledged"]
	
        print("<tr><td>", messageTime, "</td><td></td><td>", \
		user_fullname, "</td><td>", \
		mediadescription, "</td><td>", \
		sendto, "</td><td>",  \
		alertstatus_txt, "</td><td>", \
		subject, "</td></tr>")
        if status != "1":
            print("<tr><td></td><td>Error</td><td>", alerterror, "</td></tr>")

        ackBy = ""
        ackMsg = ""
        ackTime = "0"

        for ack in event[0]["acknowledges"]:
            ackClock = ack["clock"]
            ackName = ack["name"]
            ackSurname = ack["surname"]
            ackBy = ackName+" "+ackSurname
            ackMsg = ack["message"].replace('\n', '')
            ackTime = datetime.fromtimestamp(int(ackClock)).strftime('%Y-%m-%d %H:%M:%S')	
            print("<tr><td></td><td>Acknowledged</td><td>", ackBy, "</td><td>", ackTime, "</td><td colspan=3>", ackMsg, "</td></tr>")   		


print("</table>")

print("</body></html>")


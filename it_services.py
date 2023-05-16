#!/usr/bin/python3
"""
Testing SLA reporting

Parms: 1) IT Service Name

"""

from pyzabbix import ZabbixAPI
from os import environ

import sys
import datetime as datetime
import pprint as pprint

def service_rpt(sid):
    sla = zapi.service.getsla(serviceids=sid, intervals=theinterval)

    service = zapi.service.get(serviceids=sid, output="extend",
                        selectDependencies="extend",selectAlarms="extend",
                        selectTriggers="extend")
    print("<li>")
    print(service[0]["name"], end="")

    if service[0]["showsla"] == "1":
        slaf = float(sla[sid]["sla"][0]["sla"])
        goodslaf = float(service[0]["goodsla"])
        if slaf < goodslaf:
            color = "red"
        else:
            color = "green"
        print("<font color="+color+">", "%.2f" % slaf+"%", "</font>")

        if len(service[0]["alarms"]) > 0:
        
            print("<table cellpadding='1' cellspacing='1' bgcolor='#DCDCDC'>")
            print("<tr><td>Alarm Date / Time</td><td>Severity</td></tr>")
            alarmct = int(0)
            for alarm in service[0]["alarms"]:
                if float(alarm["clock"]) < start_dt.timestamp() or float(alarm["clock"]) > end_dt.timestamp():
                    continue
                alarmct += 1
                alarmtime = datetime.datetime.fromtimestamp(int(alarm["clock"])).strftime('%Y-%m-%d %H:%M:%S')
                alarmst = int(alarm["value"])
                if alarmct < 7:
                    print("<tr><td>", alarmtime, "</td><td><font color='#"+sev_color[alarmst]+"'>",
                          sev_level[alarmst], "</font></td></tr>")
            if alarmct > 6:
                skipped = alarmct - 6
                print("<tr><td colspan=2>", skipped, "Alarms not printed</td></tr>")
            print("</table>")
            print("<br>")
    else:
        print()
    

                             
    if len(service[0]["dependencies"]) > 0:
        print("<ol>")
        for service in service[0]["dependencies"]:
            service_rpt(service["serviceid"])
        print("</ol>")

    print("</li>")



#import logging
#logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)

target_its = str(sys.argv[1])
#target_its = "Lansweeper"

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = 'https://'+os.environ['Zhost']+'/zabbix'

zapi = ZabbixAPI(ZABBIX_SERVER)

# Login to the Zabbix API

zapi.login(environ['Zuser'], environ['Zpass'])

sev_color = ( "#008000", "D6F6FF", "FFF6A5", "FFB689", "FF9999", "FF3838" )
sev_level = ( "OK", "Info", "Warning", "Average", "High", "Disaster" )

service = zapi.service.get(filter={"name":target_its}, output="extend")

midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
end_dt = midnight - datetime.timedelta(datetime.date.today().weekday())
start_dt = end_dt - datetime.timedelta(7)
st = int(start_dt.strftime("%s"))
en = int(end_dt.strftime("%s"))

theinterval={"from": str(st), "to": str(en)}

print("<html>")
print("<title>IT Service report</title>")
print("<body>")
print("<h1>IT Service report</h1>")
print("Date range", start_dt, "to", end_dt)
print("<ol>")

service_rpt(service[0]["serviceid"])

print("</ol></body></html>")

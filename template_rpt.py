#!/usr/bin/python3

from pyzabbix import ZabbixAPI
import json
import pprint
from datetime import *
from operator import itemgetter
from os import environ

# import logging
# logging.basicConfig(filename='pyzabbix_debug.log',level=logging.DEBUG)

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = "https://" + environ["Zhost"] + "/zabbix"

zapi = ZabbixAPI(ZABBIX_SERVER)

# Login to the Zabbix API
zapi.login(environ["Zuser"], environ["Zpass"])

item_type = [
    "Agent",
    "notUsed",
    "Trapper",
    "Simple",
    "notUsed",
    "Internal",
    "notUsed",
    "Agent active",
    "Aggregate",
    "Web",
    "External",
    "DataBase",
    "IMPI",
    "SSH",
    "TELNET",
    "calculated",
    "JMX",
    "SNMP Trap",
    "Dependant",
    "HTTP",
    "SNMP",
]


trigger_sev = ["N/C", "Info", "Warning", "Average", "High", "Disaster"]

templates = zapi.template.get(output="extend", selectHosts="count", sortfield=["name"])

print("<html>")
print("<title>Zabbix templates</title>")
print("<body>")
print("<h1>Zabbix templates</h1>")
print("<h2>Contents</h2>")
print("<ol>")

# Create Contents

for template in templates:
    if int(template["hosts"]) > 0:
        print(
            '<li><a href="#' + template["templateid"] + '">' + template["name"] + "</a>"
        )

print("</ol>")

print("<h1>Template Details</h1>")

print("<hr>")

# Create body

for template in templates:
    if int(template["hosts"]) > 0:
        detail = zapi.template.get(
            output="extend",
            templateids=template["templateid"],
            selectGroups="extend",
            selectTemplates="extend",
            selectParentTemplates="extend",
            selectHttpTests="extend",
            selectItems="extend",
            selectDiscoveries="extend",
            selectTriggers="extend",
            selectHosts="extend",
        )

        print("<hr>")
        print(
            '<a name="' + template["templateid"] + '"</a>',
            "<h2>" + template["name"] + "</h2>",
        )

        if len(detail[0]["description"]) > 0:
            print("<b>Notes:</b>", detail[0]["description"])

        if len(detail[0]["groups"]) > 0:
            print("<h3>Groups</h3>")
            for group in detail[0]["groups"]:
                print(group["name"], "</br>")

        if len(detail[0]["parentTemplates"]) > 0:
            print("<h3>Linked templates</h3>")
            for template in sorted(detail[0]["parentTemplates"], key=itemgetter("name")):
                print(template["name"], "<br>")

        if len(detail[0]["templates"]) > 0:
            print("<h3>Linked to templates</h3>")
            for template in sorted(detail[0]["templates"], key=itemgetter("name")):
                print(template["name"], "<br>")

        if len(detail[0]["hosts"]) > 0:
            print("<h3>Linked to hosts</h3>")
            linked_hosts = len(detail[0]["hosts"])
            n = 0
            for host in sorted(detail[0]["hosts"], key=itemgetter("name")):
                print(host["name"], "<br>")
                n += 1
                if n > 9:
                    print("..... and", linked_hosts - n, "more")
                    break

        if len(detail[0]["httpTests"]) > 0:
            print("<h3>Http Tests</h3>")
            for test in detail[0]["httpTests"]:
                print(test["name"], "<br>")

        if len(detail[0]["discoveries"]) > 0:
            print("<h3>Discovery</h3>")
            print(
                "<table border=2><tr><th>Name</th><th>Key</th><th>Type<th>Interval</th></tr>"
            )
            for discovery in sorted(detail[0]["discoveries"], key=itemgetter("name")):
                print(
                    "<tr><td>"
                    + discovery["name"]
                    + "</td><td>"
                    + discovery["key_"]
                    + "</td><td>"
                    + item_type[int(discovery["type"])]
                    + "</td><td align=right>"
                    + discovery["delay"]
                    + "</td></tr>"
                )
                lld_rule = zapi.discoveryrule.get(
                    output="extend",
                    templateids=detail[0]["templateid"],
                    selectItems="extend",
                    selectTriggers="extend",
                )

                print(
                    "<tr><td align=right>Items</td><td colspan=4>",
                    "<table border=1 width=100%><tr><th>Name</th><th>Key</th><th>Interval</th><th>Type</th></tr>",
                )
                for item in sorted(lld_rule[0]["items"], key=itemgetter("name")):
                    print(
                        "<tr><td>"
                        + item["name"]
                        + "</td><td>"
                        + item["key_"]
                        + "</td><td align=right>"
                        + item["delay"]
                        + "</td><td>"
                        + item_type[int(item["type"])]
                        + "</td></tr>"
                    )
                print("</table></td></tr>")

                if len(lld_rule[0]["triggers"]) > 0:
                    print(
                        "<tr><td align=right>Triggers</td><td colspan=4>",
                        "<table border=1 width=100%><tr><th>Name</th><th>Severity</th></tr>",
                    )
                    for trigger in sorted(
                        lld_rule[0]["triggers"], key=itemgetter("description")
                    ):
                        print(
                            "<tr><td>"
                            + trigger["description"]
                            + "</td><td>"
                            + trigger_sev[int(trigger["priority"])]
                            + "</td></tr>"
                        )
                    print("</table></td></tr>")

            print("</table>")

        #     print("<tr><td colspan=4><pre>", json.dumps(trigger, indent=4, sort_keys=True), "</td></pre>")

        if len(detail[0]["items"]) > 0:
            print("<h3>Items</h3>")
            print("<table border=2>")
            print("<tr><th>Name<r/th><th>Key</th><th>Interval</th><th>Type</th></tr>")

            for item in sorted(detail[0]["items"], key=itemgetter("name")):
                print(
                    "<tr><td>"
                    + item["name"]
                    + "</td><td>"
                    + item["key_"]
                    + "</td><td align=right>"
                    + item["delay"]
                    + "</td><td>"
                    + item_type[int(item["type"])]
                    + "</td></tr>"
                )

            print("</table>")

        if len(detail[0]["triggers"]) > 0:
            print("<h3>Triggers</h3>")
            print("<table border=2>")
            print("<tr><th>Name</th><th>Severity</th></tr>")

            for trigger in sorted(detail[0]["triggers"], key=itemgetter("description")):
                print(
                    "<tr><td>"
                    + trigger["description"]
                    + "</td><td>"
                    + trigger_sev[int(trigger["priority"])]
                    + "</td></tr>"
                )

            print("</table>")

        print("<br><hr>")

#    print("<pre>")
#    if len(detail[0]['discoveries']) > 0:
#       print(json.dumps(detail, indent=4, sort_keys=True)
#    print("</pre>")

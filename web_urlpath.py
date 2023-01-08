#!/usr/bin/python3

#
# web_urlpath.py
#
# Parms 1) target host name
#       2) full url with path
#
# Updated for Zabbix 6.0
# see https://docs.python.org/3/library/urllib.parse.html
#
# Validate: 1) scheme is http or https
#           2) that there is a url path, is simple url, use web_vhost_gen
#
# Generate
#          1) Interface for dns and port (So Zabbix search by dns works)
#          2) if https, generate cert expiration test, if it doesn't already exist
#          3) web test for full url path
#          4) Tags ZBZ_Vhost : web_urlpath added


from pyzabbix import ZabbixAPI
from os import environ
from urllib.parse import urlparse
import pprint
import socket
import sys

# activate these lines for tracing
# import logging
# logging.basicConfig(filename="pyzabbix_debug.log", level=logging.DEBUG)

# The hostname at which the Zabbix web interface is available
ZABBIX_SERVER = "https://" + environ["Zhost"] + "/zabbix"
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(environ["Zuser"], environ["Zpass"])

# Command line arg is the host to process
target_host = str(sys.argv[1])
url = str(sys.argv[2])

# validate url
o = urlparse(url)

print("URL is", url, "\n")
print("extracted scheme:", o.scheme)
print("        hostname:", o.hostname)
print("            port:", o.port)
print("        url path:", o.path, "\n")

if not (o.scheme == "http" or o.scheme == "https"):
    print("Only http or https are supported")
    sys.exit(8)

if o.scheme == "http" and o.port == 80:
    print("80 is the defualt http port, remove and rerun")
    sys.exit(8)

if o.scheme == "https" and o.port == 443:
    print("443 is the defualt https port, remove and rerun")
    sys.exit(8)

# port in various formats
#   zPort: string passed to API port parameters
#   port_txt: String, null if default port, prefixed with " " if needed, ex " 8080"
#   url_port_txt: Used to build url, null if default port, prefixed wiht ":" if needed, ex ":8080"

if o.port is None:
    if o.scheme == "https":
        zPort = "443"
    if o.scheme == "http":
        zPort = "80"
    port_txt = ""
    url_port_txt = ""
else:
    zPort = str(o.port)
    port_txt = " " + str(o.port)

# get the target host, interfaces and HttpTests
host = zapi.host.get(
    filter={"host": target_host}, output="extend", selectMacros="extend",
)
# pprint.pprint(host)

# prettyHostName = name as in Zabbix, could be mIxEd case.....
if len(host) == 0:
    print("Host not found in zabbix for:", target_host)
else:
    host = host[0]
    hostId = host["hostid"]
    prettyHostName = host["host"]

if len(host["macros"]) > 0:
    host_macros = host["macros"]
else:
    host_macros = {}

zHostMacro = ""
zMacroCount = 0
zUsedMacros = []
if len(host_macros) > 0:
    for m in host_macros:
        if "{$URLPATH" in m["macro"]:
            zMacroCount += 1
            zUsedMacros.append(int(m["macro"][9:-1]))
            if url == m["value"]:
                zHostMacro = m["macro"]
                break

if zHostMacro != "":
    print("Host macro already exists:", zHostMacro)
    sys.exit(8)

# FInd available macro
for n in range(1, 100):
    if n not in zUsedMacros:
        zHostMacro = "{$URLPATH" + str(n) + "}"
        break
    if n == 99:
        print("BUG? found 99 {$URLPATHnn} macros?")
        sys.exit(16)

print("Creating new host macro:", zHostMacro)
result = zapi.usermacro.create(hostid=hostId, macro=zHostMacro, value=url)

# get base interface - maybe not needed
# base_interfaces = zapi.hostinterface.get(hostids=hostId, filter={"main": "1"})
# base_interface = base_interfaces[0]
# pprint.pprint(base_interface)

# Check for interface with DNS
interfaces = zapi.hostinterface.get(
    hostids=hostId, filter={"dns": o.hostname, "port": zPort}
)

# pprint.pprint(interfaces)

if len(interfaces) == 0:
    print("Creating host interface")
    ip = socket.gethostbyname(o.hostname)
    new_interface = zapi.hostinterface.create(
        hostid=hostId, main="0", type="1", useip="0", dns=o.hostname, ip=ip, port=zPort
    )
    interfaceId = new_interface["interfaceids"][0]
else:
    interfaceId = interfaces[0]["interfaceid"]
    print("Interface exists")

# if scheme https
if o.scheme == "https":
    #   Construct item name for potential new item
    item_name = o.hostname + port_txt + " SSL Certificate days till expiration"

    #   Does item exist?
    check_item = zapi.item.get(hostids=hostId, filter={"name": item_name})
    #   pprint.pprint(check_item)

    if len(check_item) > 0:
        print("Item exists for", item_name)
    else:
        print("Creating cert check item for", o.hostname + port_txt)
        this_key = "cert_days_left.sh[" + o.hostname + "," + zPort + "]"
        item_resp = zapi.item.create(
            {
                "name": item_name,
                "key_": this_key,
                "type": "10",
                "hostid": hostId,
                "interfaceid": interfaceId,
                "value_type": "0",
                "delay": "43200",
                "tags": [
                    {"tag": "ZBX_Vhost6", "value": "urlpath"},
                    {"tag": "Application", "value": "AppOwner Web"},
                ],
            }
        )

        #  print 'Creating < 3 day disaster trigger'
        trigger_resp = zapi.trigger.create(
            {
                "description": o.hostname
                + port_txt
                + " Certificate expires within 3 days",
                "expression": "last(/" + prettyHostName + "/" + this_key + ")<4",
                "priority": "5",
                "status": "0",
            }
        )

        #  print 'Creating < 10 day high trigger'
        trigger_resp = zapi.trigger.create(
            {
                "description": o.hostname
                + port_txt
                + " Certificate expires within 10 days",
                "expression": "last(/" + prettyHostName + "/" + this_key + ")<10",
                "priority": "4",
                "status": "0",
                "dependencies": [{"triggerid": trigger_resp["triggerids"][0]}],
            }
        )

        #  print 'Creating < 15 day average trigger'
        trigger_resp = zapi.trigger.create(
            {
                "description": o.hostname
                + port_txt
                + " Certificate expires within 15 days",
                "expression": "last(/" + prettyHostName + "/" + this_key + ")<15",
                "dependencies": [{"triggerid": trigger_resp["triggerids"][0]}],
                "priority": "3",
                "status": "0",
            }
        )

        #  print 'Creating < 30 day warning trigger'
        trigger_resp = zapi.trigger.create(
            {
                "description": o.hostname
                + port_txt
                + " Certificate expires within 30 days",
                "expression": "last(/" + prettyHostName + "/" + this_key + ")<30",
                "priority": "2",
                "dependencies": [{"triggerid": trigger_resp["triggerids"][0]}],
            }
        )


# Check if web test exists

zTestName = o.scheme + " test " + zHostMacro

web_check = zapi.httptest.get(hostids=hostId, filter={"name": zTestName},)

if len(web_check) > 0:
    print("Web test exists for", zTestName)
else:
    print("Creating web test for", zTestName)
    web_resp = zapi.httptest.create(
        {
            "name": zTestName,
            "hostid": hostId,
            "delay": "240",
            "verify_host": "1",
            "verify_peer": "1",
            "steps": [{"name": "s1", "url": url, "status_codes": "200", "no": "1",}],
            "tags": [
                {"tag": "ZBX_Vhost6", "value": "urlpath"},
                {"tag": "Application", "value": "AppOwner Web"},
            ],
        }
    )

    trigger_resp = zapi.trigger.create(
        {
            "description": "Web test failed " + zHostMacro,
            "expression": "min(/"
            + prettyHostName
            + "/web.test.fail["
            + zTestName
            + "],#2)>0",
            "priority": "4",  # 2 for testing, 4 for production
            "status": "0",
            "tags": [{"tag": "ZBX_Vhost6", "value": "urlpath"}],
        }
    )

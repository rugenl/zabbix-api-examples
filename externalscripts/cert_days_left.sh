#!/bin/bash

# Check certificate days till expiration
#
# Parms:
# $1 = DNS/IP of site
# $2 = port number 
# $3 = (Optional) Extra parms, for example "-starttls smtp"

dns=`echo $1 | cut -f 1 -d/`
echo $((($(date --date "$(date --date "$(openssl s_client -servername $dns -connect $dns:$2 $3 < /dev/null 2>&1 | sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' | openssl x509 -noout -enddate | sed -n 's/notAfter=//p')")" +%s)-$(date --date now +%s))/86400))

#!/bin/bash
echo "START"

COMMAND="/tmp/route53-ddns-client.sh --hostname ${HOSTNAME} --api-key \"${APIKEY}\" --secret \"${SECRET}\" --url ${APIURL}" 2>&1
echo "${CRON_SCHEDULE} $COMMAND" >> newcron

echo "CRONTAB"
crontab newcron

# Run once now, for good measure
eval $COMMAND

echo "CRON"
cron -f

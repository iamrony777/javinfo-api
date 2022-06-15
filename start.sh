#!/bin/bash

if [[ ${CREATE_REDIS} == 'true' ]]; then
	export REDIS_URL="redis://default:$(echo "${API_PASS}" | base64)@127.0.0.1:6379"
else
	echo
fi

if [ -n "${CAPTCHA_SOLVER_URL}" ] && [ "${CAPTCHA_SOLVER_URL}" != 'None' ]; then
	echo "* * * * 6 /usr/local/bin/python /app/src/helper/javdb_login.py" > /var/spool/cron/crontabs/root
fi

# Fetch Actress data from r18 everyday
echo "0 0 * * * /usr/local/bin/python /app/src/helper/r18_db.py" >> /var/spool/cron/crontabs/root

#Honcho start
exec honcho start

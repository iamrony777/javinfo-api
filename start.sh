#!/bin/bash

if [[ ${CREATE_REDIS} == 'true' ]]; then
	export REDIS_URL="redis://default:$(echo "${API_PASS}" | base64)@127.0.0.1:6379"
else
	echo
fi

if [ -n "${CAPTCHA_SOLVER_URL}" ] && [ "${CAPTCHA_SOLVER_URL}" != 'None' ]; then
	# Update javdb cookies at 00:00 on Sunday, ref. https://crontab.guru/every-week
	crontab -l | { cat; echo "0 0 * * 0 /usr/local/bin/python /app/src/helper/javdb_login.py"; } | crontab - 
fi

if [ -n "${HEALTHCHECK_PROVIDER}" ] && [ "${HEALTHCHECK_PROVIDER}" != 'None' ]; then
	# Healthcheck at every 15th minute, ref. https://crontab.guru/#*/15_*_*_*_*
	crontab -l | { cat; echo "*/15 * * * * /usr/local/bin/python /app/src/helper/healthcheck.py"; } | crontab -
fi

# Fetch Actress data from r18 everyday, ref. https://crontab.guru/#0_0_*_*_*
crontab -l | { cat; echo "0 0 * * * /usr/local/bin/python /app/src/helper/r18_db.py"; } | crontab -

#Honcho start
exec honcho start

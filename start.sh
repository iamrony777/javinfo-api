#!/bin/bash

#Save current time since epoch (for scripts)
echo  "{\"startup\":$(date +%s)}" > /tmp/startup

if [[ ${CREATE_REDIS} == 'true' ]]; then
	export REDIS_URL="redis://default:$(echo "${API_PASS}" | base64)@127.0.0.1:6379"
else
	echo
fi

if [ -n "${HEALTHCHECK_PROVIDER}" ] && [ "${HEALTHCHECK_PROVIDER}" != 'None' ]; then
	# Healthcheck at every 15th minute, ref. https://crontab.guru/#*/15_*_*_*_*
	crontab -l | { cat; echo "*/15 * * * * /usr/local/bin/python /app/api/scripts/ping.py"; } | crontab -
fi

# Fetch Actress data from r18 everyday, ref. https://crontab.guru/#0_0_*_*_*
crontab -l | { cat; echo "0 0 * * * /usr/local/bin/python /app/api/scripts/r18_db.py"; } | crontab -

if [ -n "${CAPTCHA_SOLVER_URL}" ] && [ "${CAPTCHA_SOLVER_URL}" != 'None' ]; then
	# Update javdb cookies at 00:00 on Sunday, ref. https://crontab.guru/every-week
	crontab -l | { cat; echo "0 0 * * 0 /usr/local/bin/python /app/api/scripts/javdb_login.py"; } | crontab - 

	# Also run same script as Startup job
	/usr/local/bin/python /app/api/scripts/javdb_login.py &
fi


# And also run as startup job
/usr/local/bin/python /app/api/scripts/r18_db.py &


# cat Procfile

#Placeholder for processmanager
exec START

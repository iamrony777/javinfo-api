#!/bin/bash

# source "${0%/*}/api/helper/color.bash"

# Save current time since epoch (for scripts)
# echo  "{\"startup\":$(date +%s)}" > /tmp/startup
if [[ -z $]]
if [[ ${PLATFORM} == 'railway' ]]; then

	if [[ ${CREATE_REDIS} == 'true' ]]; then
		export REDIS_URL="redis://default:$(echo "${API_PASS}" | base64)@127.0.0.1:6379"
	else
		echo
	fi

	if [ -n "${HEALTHCHECK_PROVIDER}" ] && [ "${HEALTHCHECK_PROVIDER}" != 'None' ]; then
		# Healthcheck at every 15th minute, ref. https://crontab.guru/#*/15_*_*_*_*
		crontab -l | { cat; echo "\"*/15 * * * *\" \"$(which python3)\" /app/api/scripts/ping.py"; } | crontab -
	fi

	# Fetch Actress data from r18 everyday, ref. https://crontab.guru/#0_0_*_*_*
	crontab -l | { cat; echo "\"0 0 * * *\" \"$(which python3)\" /app/api/scripts/r18_db.py"; } | crontab -

	if [ -n "${CAPTCHA_SOLVER_URL}" ] && [ "${CAPTCHA_SOLVER_URL}" != 'None' ]; then
		# Update javdb cookies at 00:00 on Sunday, ref. https://crontab.guru/every-week
		crontab -l | { cat; echo "\"0 0 * * 0\" \"$(which python3)\" /app/api/scripts/javdb_login.py"; } | crontab - 
	fi
else
	# Run those crontab apps but with APScheduler
	(sleep 5; /app/api/scripts/cron "0 0 * * *" "/app/api/scripts/r18_db.py") &
	(sleep 5; /app/api/scripts/cron "0 0 * * 0" "/app/api/scripts/javdb_login.py") &
	(sleep 5; /app/api/scripts/cron "*/15 * * * *" "/app/api/scripts/ping.py") &
fi 


# And also run as startup job

# RESTRUCTURE DATABASE
(sleep 10; "$(which python3)" /app/api/scripts/redis_database_setup.py ) &

# JAVDB LOGIN COOKIES
(sleep 30; HANDLER="background" "$(which python3)" /app/api/scripts/javdb_login.py) &

# GENERATE R18 ACTRESS DATABASE
(sleep 30; HANDLER="background" "$(which python3)" /app/api/scripts/r18_db.py) &

#Placeholder for processmanager
exec START

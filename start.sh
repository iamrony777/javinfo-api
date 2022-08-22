#!/bin/bash

source "/app/api/helper/color.bash"

# Save current time since epoch (for scripts)
# echo  "{\"startup\":$(date +%s)}" > /tmp/startup

if [ "${PLATFORM}" == "railway" ] || [ "${PLATFORM}" == "vps" ]; then
	echo -e "$INFO PLATFORM: $PLATFORM"
	if [[ "${CREATE_REDIS}" == "true" ]]; then
		export REDIS_URL="redis://default:$(echo "${API_PASS}" | base64)@127.0.0.1:6379"
	fi

	if [ -n "${HEALTHCHECK_PROVIDER}" ] && [ "${HEALTHCHECK_PROVIDER}" != "None" ]; then
		# Healthcheck at every 15th minute, ref. https://crontab.guru/#*/15_*_*_*_*
		crontab -l | {
			cat
			echo "\"*/15 * * * *\" \"$(which python3)\" /app/api/scripts/ping.py"
		} | crontab -
	fi

	# Fetch Actress data from r18 everyday, ref. https://crontab.guru/#0_0_*_*_*
	crontab -l | {
		cat
		echo "\"0 0 * * *\" \"$(which python3)\" /app/api/scripts/r18_db.py"
	} | crontab -

	if [ -n "${JAVDB_EMAIL}" ] && [ -n "${JAVDB_PASSWORD}" ]; then
		# Update javdb cookies at 00:00 on Sunday, ref. https://crontab.guru/every-week
		crontab -l | {
			cat
			echo "\"0 0 * * 0\" \"$(which python3)\" /app/api/scripts/javdb_login.py"
		} | crontab -
	fi
else
	# Run those crontab apps but with APScheduler
	(
		sleep 5
		/app/api/scripts/cron "0 0 * * *" "/app/api/scripts/r18_db.py"
	) &
	if [ -n "${HEALTHCHECK_PROVIDER}" ] && [ "${HEALTHCHECK_PROVIDER}" != "None" ]; then
		(
			sleep 5
			/app/api/scripts/cron "*/15 * * * *" "/app/api/scripts/ping.py"
		) &
	fi

	if [ -n "${JAVDB_EMAIL}" ] && [ -n "${JAVDB_PASSWORD}" ]; then
		(
			sleep 5
			/app/api/scripts/cron "0 0 * * 0" "/app/api/scripts/javdb_login.py"
		) &
	fi
fi

# And also run as startup job

if (/app/api/scripts/startup); then
	# RESTRUCTURE DATABASE
	(
		sleep 10
		"$(which python3)" /app/api/scripts/redis_database_setup.py
	) &
	(
		sleep 10
		HANDLER="background" "$(which python3)" /app/api/scripts/r18_db.py
	) &
	if [ -n "${JAVDB_EMAIL}" ] && [ -n "${JAVDB_PASSWORD}" ]; then # JAVDB LOGIN COOKIES
		(
			sleep 10
			HANDLER="background" "$(which python3)" /app/api/scripts/javdb_login.py
		) &
	fi
fi

#Placeholder for processmanager
exec START

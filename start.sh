#!/bin/bash

#Run-time

source "api/helper/color.bash"

# Save current time since epoch (for scripts)
# echo  "{\"startup\":$(date +%s)}" > /tmp/startup
date +%s >/tmp/startup

# BASE_URL setup
case $PLATFORM in 
railway)
	export BASE_URL=${BASE_URL:-$RAILWAY_STATIC_URL}
	echo -e "$INFO BASE_URL: $BASE_URL"
	;;
render)
	export BASE_URL=${BASE_URL:-$RENDER_EXTERNAL_URL}
	echo -e "$INFO BASE_URL: $BASE_URL"
	;;
heroku)
	export BASE_URL=${BASE_URL:-https://$APP_NAME.herokuapp.com}
	echo -e "$INFO BASE_URL: $BASE_URL"
	;;
container)
	export BASE_URL=${BASE_URL:-http://127.0.0.1:8080}
	echo -e "$INFO BASE_URL: $BASE_URL"
	;;
esac

background_tasks() {
	/app/api/scripts/cron "0 0 * * *" "/app/api/scripts/r18_db.py" &
	if [ -n "${HEALTHCHECK_PROVIDER}" ] && [ "${HEALTHCHECK_PROVIDER}" != "None" ]; then
		if [[ $PLATFORM == "render" ]]; then 
			/app/api/scripts/cron "*/10 * * * *" "/app/api/scripts/ping.py" & # Render's inactivity timeout is 15min
		else
			/app/api/scripts/cron "*/25 * * * *" "/app/api/scripts/ping.py" & # Heroku's inactivity timeout is 30min
		fi
	fi
	if [ -n "${JAVDB_EMAIL}" ] && [ -n "${JAVDB_PASSWORD}" ]; then 
		/app/api/scripts/cron "0 0 * * 0" "/app/api/scripts/javdb_login.py" &
	fi
}

startup_tasks() {
	if (/app/api/scripts/startup); then
		# RESTRUCTURE DATABASE
		"$(which python3)" /app/api/scripts/redis_database_setup.py &
		HANDLER="background" "$(which python3)" /app/api/scripts/r18_db.py &
		if [ -n "${JAVDB_EMAIL}" ] && [ -n "${JAVDB_PASSWORD}" ]; then # JAVDB LOGIN COOKIES
			HANDLER="background" "$(which python3)" /app/api/scripts/javdb_login.py &
		fi
	fi
}


# scheduling startup tasks
if [[ "$CREATE_REDIS" == "true" ]]; then
	base64_pass=$(echo "$API_PASS" | base64)
	sed -i "s/PASSWORD/$base64_pass/g" /app/conf/redis.conf
	export REDIS_URL="redis://default:$base64_pass@127.0.0.1:6379"

	(
		wait-for-it -t 0 127.0.0.1:6379
		startup_tasks
	) &
else
	startup_tasks &
fi

# scheduling background tasks
case $PLATFORM in
railway | container) # via crontab
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
	;;

render | heroku ) # via custom made python-crontab
	echo -e "$INFO PLATFORM: $PLATFORM"
	# Run those crontab apps but with APScheduler

	if [[ "$CREATE_REDIS" == "true" ]]; then
		(
			wait-for-it -t 0 127.0.0.1:6379
			background_tasks
		) &
	else
		background_tasks &
	fi
	;;
esac


# Timezone set
# setup-timezone -z "$TIMEZONE"

# Remove empty environment variable
# env | while read -r line; do 
#     var=$(echo "$line" | cut -d'=' -f 2)
#     if [[ ${#var} -eq 0 ]]; then
#         key=$(echo -e "$(echo "$line" | cut -d'=' -f 1)")
#         echo -e "$WARNING Removing '$key'"
#         unset "$key"
#     fi
# done

#Placeholder for processmanager
exec START
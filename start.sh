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
	export BASE_URL=${BASE_URL:-http://127.0.0.1:$PORT}
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

downloader() {
	wget -cqS --header "Authorization: Basic $(echo -n "${API_USER}":"${API_PASS}" | base64)" -O "$1" "$2"
	return $?
}

# Platform dependent configs
case $PLATFORM in
"railway" | "render" | "container")
	if [[ ${CREATE_REDIS} == "true" ]]; then
		echo -e "$INFO Creating redis server, please wait..."
		apk add --no-cache redis
		echo -e "$INFO Adding redis-server to Procfile..."
		sed -i 's|redis_process_placeholder|redis: redis-server \/app\/conf\/redis.conf|g' /app/Procfile
	else
		echo -e "$INFO Using redis server from plugins / addons"
		sed -i 's|redis_process_placeholder||g' /app/Procfile
	fi

	case "$PLATFORM" in
	"railway")
		echo -e "$INFO PLATFORM: $PLATFORM"
		export BASE_URL=${BASE_URL:-$RAILWAY_STATIC_URL}/api/database
		echo -e "$INFO Restoring database from ${BASE_URL}"

		if downloader "/data/database.rdb" "${BASE_URL}"; then
			echo -e "$SUCCESS Database Restored"
		else
			echo -e "$WARNING Failed to restore database from $BASE_URL"
			rm -rf /data/database.rdb
		fi
		;;
	"render")
		echo -e "$INFO PLATFORM: $PLATFORM"
		if [[ $PLATFORM == "render" ]]; then
			export BASE_URL=${BASE_URL:-$RENDER_EXTERNAL_URL}/api/database
			echo -e "$INFO Restoring database from ${BASE_URL}"

			if downloader "/data/database.rdb" "${BASE_URL}"; then
				echo -e "$SUCCESS Database Restored"
			else
				echo -e "$WARNING Failed to restore database from $BASE_URL"
				rm -rf /data/database.rdb
			fi
		fi
		;;
	"container")
		echo -e "$INFO PLATFORM: $PLATFORM"
		echo -e "$INFO Local deploy should use persistance storage, not restoring database from url"
		;;
	esac

	sed -i "s|api:|api: PORT=$PORT|g" /app/Procfile
	;;
"heroku")
	echo -e "$WARNING Not creating any database!"
	sed -i 's|redis_process_placeholder||g' /app/Procfile

	# Crontab also doesn't work on heroku
	sed -i 's|cronjob: crond -f||g' /app/Procfile
	echo -e "$INFO Port will be set during startup"
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
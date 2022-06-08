#!/bin/bash

download_database() {
	wget --quiet --user "${API_USER}" --password "${API_PASS}" -O /app/src/database.rdb "$1" ; return $?
}

if [[ ${CREATE_REDIS} == 'true' ]]; then
	echo -e "[INFO] Creating redis server, please wait..."
	apk add --no-cache redis &&
		sed -i 's/PASSWORD/'"$(echo "${API_PASS}" | base64)"'/g' src/conf/redis.conf
	echo -e "[INFO] Adding redis-server to Procfile..."
	echo "db: redis-server ./src/conf/redis.conf" >> Procfile

	if [[ -n ${RAILWAY_STATIC_URL} ]]; then
		echo -e "[INFO] Restoring database from ${RAILWAY_STATIC_URL}/database"
		URL="${RAILWAY_STATIC_URL}/database"
		apk add --no-cache wget && \
		mkdir -p /app/src && \
		if download_database "${URL}"; then
			echo "[INFO] Database Restored"
		else
			echo "[ERROR] Failed to restore database"
			rm -rf /app/src/database.rdb
		fi
	fi

else
	echo "[INFO] Using redis server from plugins / addons"
fi


echo PORT="${PORT}" >>.env

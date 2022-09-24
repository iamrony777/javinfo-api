#!/bin/bash

# Build-time

source "api/helper/color.bash"

mkdir -p /data/

wget -q -O "/app/wait-for-it" "https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh"
mv "/app/wait-for-it" "/usr/local/bin/wait-for-it" && chmod 755 "/usr/local/bin/wait-for-it"

downloader() {
	wget -cqS --header "Authorization: Basic $(echo -n "${API_USER}":"${API_PASS}" | base64)" -O "$1" "$2"
	return $?
}

#HEROKU / RAILWAY dependent configs
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

arch=$(uname -m)
overmind_version=$(curl -s https://api.github.com/repos/DarthSim/overmind/releases/latest | jq -r .tag_name)
case ${arch} in
x86_64)
	echo -e "$INFO Installing Overmind for ${arch}"
	overmind_file=overmind-${overmind_version}-linux-amd64.gz
	wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
	gunzip overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
	sed -i 's|START|overmind start|g' /app/start.sh
	;;
aarch64*)
	echo -e "$INFO Installing Overmind for ${arch}"
	overmind_file=overmind-${overmind_version}-linux-arm64.gz
	wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
	gunzip overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
	sed -i 's|START|overmind start|g' /app/start.sh
	;;
arm*)
	echo -e "$INFO Installing Overmind for ${arch}"
	overmind_file=overmind-${overmind_version}-linux-arm.gz
	wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
	gunzip overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
	sed -i 's|START|overmind start|g' /app/start.sh
	;;
*)
	echo -e "$INFO Installing Honcho for ${arch}"
	pip install --no-cache-dir honcho
	sed -i 's|START|honcho start|g' /app/start.sh
	;;
esac

# Removing packages
apk del curl jq

#copy images: /app/api/html/images/* -> /app/docs/images/
mkdir -p /app/docs/images/
cp -r /app/api/html/images/* /app/docs/images/

#Make all scripts executable
chmod +x /app/api/scripts/*

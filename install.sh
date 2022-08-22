#!/bin/bash

source "${0%/*}/api/helper/color.bash"

downloader() {
	wget --quiet --timeout 60 --user "${API_USER}" --password "${API_PASS}" -O "$1" "$2"; return $?
}

#HEROKU / RAILWAY dependent configs
if [[ ${PLATFORM} == 'railway' ]]; then
	# Install and Setup Redis if needed
	if [[ ${CREATE_REDIS} == 'true' ]]; then
		echo -e "$INFO Creating redis server, please wait..."
		apk add --no-cache redis &&
			sed -i 's/PASSWORD/'"$(echo "${API_PASS}" | base64)"'/g' /app/conf/redis.conf
		echo -e "$INFO Adding redis-server to Procfile..."
		sed -i 's/redis_process_placeholder/redis: redis-server \/app\/conf\/redis.conf/g' /app/Procfile

		if [[ -n ${RAILWAY_STATIC_URL} ]]; then
			echo -e "$INFO Restoring database from ${RAILWAY_STATIC_URL}/database"
			URL="https://${RAILWAY_STATIC_URL}/database"
			if downloader "/app/database.rdb" "${URL}" ; then
				echo -e "$SUCCESS Database Restored"
			else
				echo -e "$WARNING Failed to restore database from $URL"
				rm -rf /app/database.rdb
			fi
		fi

	else
		echo -e "$INFO Using redis server from plugins / addons"
		sed -i 's/redis_process_placeholder//g' /app/Procfile
		
	fi

	# Restoring previous logs
	URL="https://${RAILWAY_STATIC_URL}/logs"
	if downloader "/app/javinfo.log" "${URL}"; then
		echo -e "$SUCCESS Previous logs restored"
	else
		echo -e "$WARNING Failed to restore previus logs"
		rm -rf /app/javinfo.log
	fi

	# Setting correct api port
	sed -i "s/api:/api: PORT=${PORT}/g" /app/Procfile
fi

if [[ ${PLATFORM} == 'heroku' ]]; then
	echo -e "$WARNING Not creating any database!"
	sed -i 's/redis_process_placeholder//g' /app/Procfile

	# Crontab also doesn't work on heroku
	sed -i 's/cronjob: crond -f//g' /app/Procfile
	echo -e "$INFO Port will be set during startup"
	
fi

arch=$(uname -m)
overmind_version=$(curl -s https://api.github.com/repos/DarthSim/overmind/releases/latest | jq -r .tag_name)
case ${arch} in

    x86_64)
        echo -e "$INFO Installing Overmind for ${arch}"
		overmind_file=overmind-${overmind_version}-linux-amd64.gz
		wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
		gunzip overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
		sed -i 's/START/overmind start/g' /app/start.sh
        ;;
    aarch64*)
        echo -e "$INFO Installing Overmind for ${arch}"
		overmind_file=overmind-${overmind_version}-linux-arm64.gz
		wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
		gunzip overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
		sed -i 's/START/overmind start/g' /app/start.sh
        ;;
    arm*)
        echo -e "$INFO Installing Overmind for ${arch}"
		overmind_file=overmind-${overmind_version}-linux-arm.gz
		wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
		gunzip overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
		sed -i 's/START/overmind start/g' /app/start.sh
        ;;
	*)
	    echo -e "$INFO Installing Honcho for ${arch}"
		pip install honcho==1.1.0
		sed -i 's/START/honcho start/g' /app/start.sh
		;;
esa

# Removing packages
apk del wget curl jq

#copy images: /app/api/html/images/* -> /app/docs/images/
mkdir -p /app/docs/images/
cp -r /app/api/html/images/* /app/docs/images/

#Make all scripts executable 
chmod +x /app/api/scripts/*


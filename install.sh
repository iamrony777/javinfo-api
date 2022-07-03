#!/bin/bash

downloader() {
	wget --quiet --timeout 30 --user "${API_USER}" --password "${API_PASS}" -O "$2" "$1" ; return $?
}


# Install and Setup Redis if needed
if [[ ${CREATE_REDIS} == 'true' ]]; then
	echo -e "[INFO] Creating redis server, please wait..."
	apk add --no-cache redis &&
		sed -i 's/PASSWORD/'"$(echo "${API_PASS}" | base64)"'/g' /app/conf/redis.conf
	echo -e "[INFO] Adding redis-server to Procfile..."
	sed -i 's/redis_process_placeholder/redis: redis-server \/app\/conf\/redis.conf/g' /app/Procfile

	if [[ -n ${RAILWAY_STATIC_URL} ]]; then
		echo -e "[INFO] Restoring database from ${RAILWAY_STATIC_URL}/database"
		URL="https://${RAILWAY_STATIC_URL}/database"
		if downloader "${URL}" "/app/database.rdb"; then
			echo "[INFO] Database Restored"
		else
			echo "[ERROR] Failed to restore database"
			rm -rf /app/database.rdb
		fi
	fi

else
	echo "[INFO] Using redis server from plugins / addons"
	sed -i 's/redis_process_placeholder//g' /app/Procfile
	
fi

# Restoring previous logs
URL="https://${RAILWAY_STATIC_URL}/logs"
if downloader "${URL}" "/app/javinfo.log"; then
	echo "[INFO] Previous logs restored"
else
	echo "[WARNING] Failed to restore previus logs"
	rm -rf /app/javinfo.log
fi

# Installing Deps (conditional)
arch=$(uname -m)
overmind_version=$(curl -s https://api.github.com/repos/DarthSim/overmind/releases/latest | jq -r .tag_name)
case ${arch} in

    x86_64)
        echo "[INFO] Installing Deps for ${arch}"
		overmind_file=overmind-${overmind_version}-linux-amd64.gz
		wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
		tar -xzvf overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
		sed -i 's/START/overmind start/g' /app/start.sh

        ;;
    aarch64*)
        echo "[INFO] Installing Deps for ${arch}"
		overmind_file=overmind-${overmind_version}-linux-arm64.gz
		wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
		tar -xzvf overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
		sed -i 's/START/overmind start/g' /app/start.sh

		# Pillow deps
		apk add --no-cache --virtual .pillow_ext $PILLOW_BUILD
        ;;
    arm*)
        echo "[INFO] Installing Deps for ${arch}"
		overmind_file=overmind-${overmind_version}-linux-arm.gz
		wget -qcO overmind.gz https://github.com/DarthSim/overmind/releases/download/"${overmind_version}"/"${overmind_file}"
		tar -xzvf overmind.gz && mv overmind /usr/bin/overmind && chmod 755 /usr/bin/overmind
		sed -i 's/START/overmind start/g' /app/start.sh

		# Pillow deps
		apk add --no-cache --virtual .pillow_ext $PILLOW_BUILD
        ;;
	*)
	    echo "[INFO] Installing Deps for ${arch}"
		pip install honcho==1.1.0
		sed -i 's/START/'"honcho start"'/g' /app/start.sh

		# Pillow deps
		apk add --no-cache --virtual .pillow_ext $PILLOW_BUILD
		;;
esac



# Setting correct api port
sed -i "s/api:/api: PORT=${PORT}/g" /app/Procfile


#copy images: /app/api/html/images/* -> /app/docs/images/
mkdir -p /app/docs/images/
cp -r /app/api/html/images/* /app/docs/images/
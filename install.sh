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
	echo "redis: redis-server /app/conf/redis.conf" >> Procfile

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
fi

# Restoring previous logs
URL="https://${RAILWAY_STATIC_URL}/logs"
if downloader "${URL}" "/app/javinfo.log"; then
	echo "[INFO] Previous logs restored"
else
	echo "[WARNING] Failed to restore previus logs"
	rm -rf /app/javinfo.log
fi

# Installing Exo or Honcho as process manager depending on arch
exo_version=$(curl -s https://api.github.com/repos/deref/exo/releases/latest | jq -r .tag_name)
arch=$(uname -m)
case ${arch} in

    x86_64)
        echo "[INFO] Installing Exo for ${arch}"
        exo_file=exo_${exo_version}_linux_amd64.apk
        ;;
    aarch64*)
        echo "[INFO] Installing Exo for ${arch}"
        exo_file=exo_${exo_version}_linux_arm64.apk
        ;;
    *)
        echo "[INFO] Installing Honcho"
        ;;
esac

# During arm* docker builds some python packeges requires Rust and Cargo to compile extensions
case ${arch} in
    x86_64)
		echo
		;;
	*)
		apk add --no-cache --virtual .build_ext rust cargo
		;;
esac


if [[ -n "${exo_file}" ]]; then
    wget -q https://github.com/deref/exo/releases/download/"${exo_version}"/"${exo_file}"
    apk add --allow-untrusted ./"${exo_file}"
	sed -i 's/START/'"exo run"'/g' /app/start.sh
else
    pip install honcho==1.1.0
	echo PORT="${PORT}" >>.env
	sed -i 's/START/'"honcho start"'/g' /app/start.sh
fi

# Setting correct api port
sed -i "s/api:/api: PORT=${PORT}/g" /app/Procfile

#copy images: /app/api/html/images/* -> /app/docs/images/
mkdir -p /app/docs/images/
cp -r /app/api/html/images/* /app/docs/images/
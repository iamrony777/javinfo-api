#!/bin/bash

# Build-time

source "api/helper/color.bash"

mkdir -p /data/

wget -q -O "/app/wait-for-it" "https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh"
mv "/app/wait-for-it" "/usr/local/bin/wait-for-it" && chmod 755 "/usr/local/bin/wait-for-it"

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

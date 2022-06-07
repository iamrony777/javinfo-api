#!/bin/bash

if [[ ${CREATE_REDIS} == 'true' ]]; then
	export REDIS_URL="redis://default:$(echo "${API_PASS}" | base64)@127.0.0.1:6379"
else
	echo
fi

#Honcho start
exec honcho start

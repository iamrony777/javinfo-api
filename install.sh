#!/bin/bash

if "$CREATE_REDIS" == 'true'; then
    echo -e "[INFO] Creating redis server, please wait..."
    apk add --no-cache redis && \
    echo "export REDIS_URL="redis://default:$( echo $API_PASS | base64 )@127.0.0.1:6379"" >> ~/.bashrc && \
    sed -i 's/PASSWORD/'"$( echo $API_PASS | base64 )"'/g' src/conf/redis.conf

    echo -e "[INFO] Adding redis-server to Procfile..."
    echo "db: redis-server ./src/conf/redis.conf" >> Procfile
else
    echo "[INFO] Using redis server from plugins / addons"
fi

echo "PORT=$PORT" >> .env

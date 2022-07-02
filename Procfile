api: PORT=9000 python main.py
cronjob: crond -f
caddy: caddy run -config='conf/Caddyfile' -adapter=caddyfile
ttyd: PORT=9080 ttyd -p $PORT -u $(id -u) -g $(id -u) -c $API_USER:$API_PASS bash

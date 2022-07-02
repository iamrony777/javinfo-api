api: PORT=9000 python main.py
cronjob: crond -f
caddy: caddy run -config='conf/Caddyfile' -adapter=caddyfile
ttyd: ttyd -p 9080 -u $(id -u) -g $(id -u) -c $API_USER:$API_PASS bash

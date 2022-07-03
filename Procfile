caddy: caddy run -config='conf/Caddyfile' -adapter=caddyfile
api: PORT=9000 python main.py
cronjob: crond -f
ttyd: ttyd -p 9100 -u $(id -u) -g $(id -u) bash

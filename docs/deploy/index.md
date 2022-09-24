# Common Configurations

## Variables / Options Descriptions
> **Required**

- `PORT` : Starting port, api will listen on this port only (default port `8000`, host `0.0.0.0`, don't set if using *Heroku*)
- `API_USER` & `API_PASS` : Using basic http auth to protect core endpoints , use unique password (don't use `admin` & `admin` , default is `admin` & `admin`)
- `CREATE_REDIS` : `false` (default), Check [here](#using-without-redis-database-plugin-optional)
- `LOG_REQUESTS` : `false`(default)

> Optional

- `INACTIVITY_TIMEOUT` (second): By default the Uvicorn worker will restart (to clear ram) after `300` seconds (default) if there is no request.

- `IPINFO_TOKEN`: For IP logging purposes
- `REMEMBER_ME_TOKEN` & `JDB_SESSION` : Some cotent on JAVDB requires account to view (scrape),if any result from JAVDB return `null` then maybe you need to fill up this

      - These are cookie values, login into javdb and copy values from `_jdb_session` & `remember_me_token`. This cookies will expire after 7 days if you checked _Keep me logged in for 7 days_ during sign in

- `JAVDB_EMAIL` & `JAVDB_PASSWORD`: For auto-login into JAVDB account, some query on JAVDB required login , captcha is bypassed via another api, check [repo here](https://github.com/iamrony777/captcha-solver-api)

- `CAPTCHA_SOLVER_URL`: `https://captcha-solver-api2.herokuapp.com/javdb` Check [repo](https://github.com/iamrony777/captcha-solver-api)

>> Healthcheck (Optional)

- `HEALTHCHECK_PROVIDER` :
    * `None` (default)
    * [`uptimekuma`](https://uptime.kuma.pet/) (push method)
    * [`healthchecksio`](https://healthchecks.io/)
    * `self` (ping to public url, needed `BASE_URL` env)
    * `local` (docker healthcheck)

- `UPTIMEKUMA_PUSH_URL` : Set this url in this format _`https://uptime-kuma-instance-url/api/push/monitor-slug`_ with or without optional parameters and set `HEALTHCHECK_PROVIDER` to `uptimekuma`


- `HEALTHCHECKSIO_PING_URL`: Set url in this format, _`https://healthchecks-io-instance-url/monitor-uuid`_ or _`https://healthchecks-io-instance-url/ping-key/monitor-name`_ and set `HEALTHCHECK_PROVIDER` to `healthchecksio`

>> Log request _(Optional)_

- Set `LOG_REQUEST=true` to log incoming request headers, query parameters, time, ip address details from [ipinfo](https://ipinfo.io)
- Set `IPINFO_TOKEN` with API token from [ipinfo.io](https://ipinfo.io/account) _(Optional)_

??? example "LOG Example"
    ```json
    {
        "query": {
            "id": "EBOD-391"
        },
        "method": "POST",
        "path": "/search",
        "headers": {
            "host": "(BASE_URL)",
            "accept-encoding": "gzip, deflate",
            "accept": "*/*",
            "content-length": "0",
            "authorization": "(BASIC AUTH)",
            "user-agent": "HTTPie/3.2.1",
            "x-forwarded-for": "(IP ADDRESS)",
            "x-forwarded-proto": "https",
            "x-envoy-external-address": "(IP ADDRESS)",
            "x-request-id": "XXX-XXX-XXX-XXX"
        },
        "user": {
            "ip": "(IP ADDRESS)",
            "hostname": "XXX",
            "city": "XXX",
            "region": "XXX",
            "country": "XXX",
            "loc": "XXX, XXX",
            "org": "XXX",
            "postal": "XXX",
            "timezone": "XXX/XXX"
        },
        "time": "2022-05-28 03:08:58"
    }
    ```

## Using without Redis Database Plugin _(Optional)_

=== "Creating an Ephemeral redis server"
    _(Example:  [All-in-One Template](https://railway.app/new/template/BiOVQM?referralCode=8NonTm))_

    - Set `CREATE_REDIS=true` in variables
    - using __redis.conf__ from `conf/redis.conf`
    - _DO NOT SET PASSWORD in redis.conf, REDIS_PASS = ```echo $API_PASS | base64```_

    !!! info "Note"
        On every push / build a previous copy of local-database (via `/database` endpoint)will be downloaded automatically (if available) and restored

    !!! caution "An ephemeral redis server can't be accessed from outside app container"

        > To access the database you need to download the whole database and restore locally

        send a __GET__ request to `/database` endpoint with `API_USER` and `API_PASS` as HTTP basicauth to download database.rdb file

        Example:

        >Download database.rdb file

        ```shell
        https --auth "$API_USER":"$API_PASS" --download BASE_URL/api/database
        ```
        or

        ```shell
        wget --user "$API_USER" --password "$API_PASS"  BASE_URL/api/database
        ```

        >Restore with redis-server

        ```bash
        redis-server --dbfilename database.rdb --dir "$PWD"
        ```

=== "Using selfhosted / hosted redis server"
    - Set `CREATE_REDIS=false`
    - Set `REDIS_URL=<redis_connection_string>` with your redis-server credentials <a href="https://metacpan.org/pod/URI::redis#redis://HOST[:PORT][?db=DATABASE[&password=PASSWORD]]" target="_blank">Example Connection String</a>

        - For SSL enabled connections use `rediss://` instead of `redis://` in connection string

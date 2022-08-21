# Deploy

## Using [Railway](https://railway.app)


### Automatic way `(One-Click Template  button)`

=== "With Redis Database Plugin _(Default)_"
    - Check [Variables](#variable-template) 

    [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/T55Se3?referralCode=8NonTm)

=== "Without Redis Database Plugin _(Optional)_"

    - Check [Variables](#variable-template) 
    - [What is this ?](#using-without-redis-database-plugin-optional)

    [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/BiOVQM?referralCode=8NonTm)




### Manual way `(git, railway-cli)`
1. Install [Railway-CLI](https://docs.railway.app/develop/cli)
2. Clone [Repo](https://github.com/iamrony777/javinfo-api)
    <!-- trunk-ignore(markdownlint/MD046) -->
    ```bash
    git clone https://github.com/iamrony777/javinfo-api
    ```
3. Login into Railway account, create a new project
    <!-- trunk-ignore(markdownlint/MD046) -->
    ```bash
    cd javinfo-api 
    railway login # login into railway account
    railway init # set project name and create an empty service from browser
    ```
4. Add a empty Service
    * Top-right button `+`
    * Select `Empty Service`

5. Add a Database service
    * Top-right button `+`
    * Select __Redis__

5. Set Environment Variables via RAW Editor
    * Click on __Newly created service__ _(Not the database)_
    * __Variables__ Tab -> RAW Editor

    #### __Variable template__ 

    _(just copy-paste and edit variables , railway will automatically remove comments)_
    ```bash
    # Requrired
    PORT='8000' # default starting port
    API_USER='' # HTTP basicauth : username
    API_PASS='' # HTTP basicauth : passsword
    CREATE_REDIS='false' # check #using-without-redis-database-plugin
    LOG_REQUEST='false' # check #log-requests 

    # JAVDB Search Related 
    CAPTCHA_SOLVER_URL='https://captcha-solver-api2.herokuapp.com' 
    JAVDB_EMAIL='' # Add JAVDB email / Leave empty
    JAVDB_PASSWORD='' # Add JAVDB password / Leave empty

    # OPTIONAL 
    REMEMBER_ME_TOKEN='' 
    JDB_SESSION=''
    IPINFO_TOKEN=''
    INACTIVITY_TIMEOUT='300' 
    TIMEZONE='UTC'
    REDIS_URL=''  # If already got a redis-server , then paste redis connect string here ex. redis://...

    # HEALTHCHECK (Optional)
    HEALTHCHECK_PROVIDER='None' # 'uptimekuma' for UptimeKuma Push , 'healthchecksio' for Healthchecks.io
    UPTIMEKUMA_PUSH_URL='' # https://<uptime-kuma-instance-url>/api/push/<monitor-slug> with or without optional parameters
    HEALTHCHECKSIO_PING_URL='' # https://<healthchecks-io-instance-url>/<monitor-uuid> or https://<healthchecks-io-instance-url>/<ping-key>/<monitor-name>

    # RAILWAY PROVIDED VARIABLES
    RAILWAY_STATIC_URL='' # Leave empty for default value
    BASE_URL='' # https://example.com / Publicly available url

    ```

    #### Using without Redis Database Plugin _(Optional)_

    === "Creating an Ephemeral redis server" 
        _(Example:  [All-in-One Template](https://railway.app/new/template/BiOVQM?referralCode=8NonTm))_

        - Set `CREATE_REDIS='true'` in variables
        - using __redis.conf__ from `src/conf/redis.conf`
        - _DO NOT SET PASSOWORD IN redis.conf, REDIS_PASSWORD is ```echo ${API_PASS} | base64```_

        !!! info "Note" 
            On every push / build a previous copy of local-database (via `/database` endpoint) [will be downloaded automatically](https://github.com/iamrony777/JavInfo-api/blob/main/install.sh) (if available) and restored

        !!! caution "An ephemeral redis server can't be accessed from outside app container"

            > To access the database you need to download the whole database and restore locally
        
            send a __GET__ request to `/database` endpoint with `API_USER` and `API_PASS` as HTTP basicauth to download database.rdb file

            Example:
            ##### 1. Download database.rdb file

            ```shell
            https --auth 'API_USER:API_PASS' --download API_URL/database
            ```

            ##### 2. Restore with redis-server
            ```bash
            redis-server --dbfilename database.rdb --dir /path/to/database/dir/
            ```

    === "Using selfhosted / hosted redis server"
        - Set `CREATE_REDIS='false'`
        - Set `REDIS_URL=redis://$REDIS_USER:$REDIS_PASSWORD@$REDIS_HOST:$REDIS_PORT` with your redis-server credentials


## Using [Heroku](https://heroku.com)



#### ADD TO Docs 
    ---
    #### Log requests _(Optional)_
    - Set `LOG_REQUEST='true'` to log incoming request headers, query parameters, time, ip address details (from [ipinfo](https://ipinfo.io))
    - Set `IPINFO_TOKEN` with API token from [ipinfo.io](https://ipinfo.io/account) _(Optional)_

    !!! example "LOG Example"
        ```json
        {
            "query": {
                "id": "EBOD-391"
            },
            "method": "POST",
            "path": "/search",
            "headers": {
                "host": "(API_URL)",
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



# Deploy

## Using [Railway](https://railway.app)


### Automatic way `(One-Click Template  button)`

=== "With Redis Database Plugin _(Default)_"
    - Check [Variables](#variable-template) 
<a href="https://railway.app/new/template/T55Se3?referralCode=8NonTm">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a> 


=== "Without Redis Database Plugin _(Optional)_"

    - Check [Variables](#variable-template) 
    - [What is this ?](#using-without-redis-database-plugin-optional)
<a href="https://railway.app/new/template/BiOVQM?referralCode=8NonTm">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a> 




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
    PORT="8000" # default starting port
    API_USER="" # HTTP basicauth : username
    API_PASS="" # HTTP basicauth : passsword
    CREATE_REDIS="false" # check #using-without-redis-database-plugin
    LOG_REQUEST="false" # check #log-requests 
    PLATFORM="railway"

    # JAVDB Search Related 
    CAPTCHA_SOLVER_URL="https://captcha-solver-api2.herokuapp.com" 
    JAVDB_EMAIL="" # Add JAVDB email / Leave empty
    JAVDB_PASSWORD="" # Add JAVDB password / Leave empty

    # OPTIONAL 
    REMEMBER_ME_TOKEN="" 
    JDB_SESSION=""
    IPINFO_TOKEN=""
    INACTIVITY_TIMEOUT="300" 
    TIMEZONE="UTC"
    REDIS_URL=""  # If already got a redis-server , then paste redis connect string here ex. redis://...
    BASE_URL=${RAILWAY_STATIC_URL:-} 

    # HEALTHCHECK (Optional)
    HEALTHCHECK_PROVIDER="None" # "uptimekuma" for UptimeKuma Push , "healthchecksio" for Healthchecks.io, or just `self`
    UPTIMEKUMA_PUSH_URL="" # https://<uptime-kuma-instance-url>/api/push/<monitor-slug> with or without optional parameters
    HEALTHCHECKSIO_PING_URL="" # https://<healthchecks-io-instance-url>/<monitor-uuid> or https://<healthchecks-io-instance-url>/<ping-key>/<monitor-name>

    # RAILWAY PROVIDED VARIABLES
    RAILWAY_STATIC_URL="" # Leave empty for default value

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


### Automatic way `(One-Click Template  button)`

<a href="https://heroku.com/deploy?template=https://github.com/iamrony777/JavInfo-api" target="_blank">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
</a>

### Manual way `(git + Heroku CLI)`

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli)
2. Clone [Repo](https://github.com/iamrony777/javinfo-api)
    ```bash
    git clone https://github.com/iamrony777/javinfo-api
    ```
3. Login into Railway account, create a new app
    ```bash
    cd javinfo-api 
    heroku login # Finish login process
    heorku create # You're app name will be shown here
    heroku git:remote --app $APP_NAME
    heroku stack:set container --app $APP_NAME
    ```
4. Add Database Addon _(Optional if you already using any Online redis service eg. Redislab, Upstash etc)_

    **Using [Upstash-Redis Addon](https://elements.heroku.com/addons/upstash-redis)**
    ```bash
    heroku addons:create upstash-redis:free --as REDIS --app $APP_NAME
    ```
5. Set Environmental Variables 
   ```bash
    heroku config:edit --app $APP_NAME 
   ```

    #### __Variable template__ 

    _(just copy-paste and edit variables , railway will automatically remove comments)_
    ```bash
    API_USER=""
    API_PASS=""
    CREATE_REDIS="false"
    LOG_REQUEST="false"
    PLATFORM="heroku"
    CAPTCHA_SOLVER_URL="https://captcha-solver-api2.herokuapp.com" 
    JAVDB_EMAIL=""
    JAVDB_PASSWORD=""
    REMEMBER_ME_TOKEN="" 
    JDB_SESSION=""
    IPINFO_TOKEN=""
    INACTIVITY_TIMEOUT="60" 
    TIMEZONE="UTC"
    HEALTHCHECK_PROVIDER="None"
    UPTIMEKUMA_PUSH_URL=""
    HEALTHCHECKSIO_PING_URL=""
    ```

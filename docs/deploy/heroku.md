### Automatic way `(One-Click Template  button)`

* Check [Variables](#variable-template)
* If you are using a heroku-addon as redis database , then first set an empty string in `REDIS_URL` then follow step **4.a** from
[Manual way](#manual-way-git-heroku-cli)

<a href="https://heroku.com/deploy?template=https://github.com/iamrony777/JavInfo-api" target="_blank">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
</a>

### Manual way `(git + Heroku CLI)`

1. Install <a href="https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli" target="_blank">Heroku CLI</a>
2. Clone [Repo](https://github.com/iamrony777/javinfo-api)
    ```bash
    git clone https://github.com/iamrony777/javinfo-api
    ```
3. Login into Railway account, create a new app
    ```bash
    cd javinfo-api 
    APP_NAME=""  # set app name as variable 
    heroku login # Finish login process
    heroku apps:create $APP_NAME 
    heroku git:remote --app $APP_NAME
    heroku stack:set container --app $APP_NAME
    ```
4. Using persistence database Addon _(optional if you already using any Online redis service eg. Redislab, Upstash etc)_

    1. [Upstash-Redis Addon](https://elements.heroku.com/addons/upstash-redis) _(heroku verified account required)_
        ```bash
        heroku addons:create upstash-redis:free --as REDIS --app $APP_NAME
        ```
        ** must add addon with `--as REDIS` parameter

    2. **Free hosted database**

        1. <a href="https://upstash.com/" target="_blank">Upstash</a>
        2. <a href="https://redis.com/try-free/" target="_blank">RedisLabs</a>

        Create a [redis uri](./index.md#using-without-redis-database-plugin-optional) from USERNAME , PASSWORD , HOST , PORT provided from server and modify environment variables

        ```bash
        heroku config:set --app $APP_NAME REDIS_URL=<connection-url>
        ```


5. Set Environmental Variables 


    #### __Variable template__ 

    *(copy-paste, edit and __remove__ empty variables)*

    `API_USER` & `API_PASS` are required to start the server and it is recommened to set `APP_NAME` also. _(set `REDIS_URL` if not using upstash-redis addon)_
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
    TZ="UTC"
    HEALTHCHECK_PROVIDER="None"
    UPTIMEKUMA_PUSH_URL=""
    HEALTHCHECKSIO_PING_URL=""
    APP_NAME=""
    ```

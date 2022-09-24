### Automatic way `(One-Click Template  button)`

=== "With Redis Database Plugin _(Default)_"
    - Check [Variables](#variable-template)
<a href="https://railway.app/new/template/T55Se3?referralCode=8NonTm" target="_blank">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a>


=== "Without Redis Database Plugin _(Optional)_"

    - Check [Variables](#variable-template)
    - [What is this ?](./index.md#using-without-redis-database-plugin-optional)
<a href="https://railway.app/new/template/BiOVQM?referralCode=8NonTm" target="_blank">
    <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a>




### Manual way `(git, railway-cli)`
1. Install <a href="https://docs.railway.app/develop/cli" target="_blank">Railway CLI</a>
2. Clone this [Repo](https://github.com/iamrony777/javinfo-api)
    <!-- trunk-ignore(markdownlint/MD046) -->
    ```bash
    git clone https://github.com/iamrony777/javinfo-api
    ```
3. Login into Railway account, create a new project
    <!-- trunk-ignore(markdownlint/MD046) -->
    ```bash
    cd javinfo-api
    railway login # login into railway account
    railway init # set and create new project name
    ```
4. Add a Database service
    * Top-right button `+`
    * Select __Redis__

5. Set Environment Variables via RAW Editor
    * Click on __Newly created service__ _(Not the database)_
    * __Variables__ Tab -> RAW Editor

    ---
    #### __Variable template__ 

    _(just copy-paste and edit variables , railway will automatically remove comments)_
    ```bash
    # Requrired
    PORT="8000"
    API_USER=""
    API_PASS=""
    CREATE_REDIS="false" 
    LOG_REQUEST="false"
    PLATFORM="railway"

    # JAVDB Search Related
    CAPTCHA_SOLVER_URL="https://captcha-solver-api2.herokuapp.com"
    JAVDB_EMAIL="" 
    JAVDB_PASSWORD="" 

    # OPTIONAL
    REMEMBER_ME_TOKEN=""
    JDB_SESSION=""
    IPINFO_TOKEN=""
    INACTIVITY_TIMEOUT="300"
    TZ="UTC"
    REDIS_URL=""  # If already got a redis-server , then paste redis connect string here ex. redis://...
    BASE_URL=${RAILWAY_STATIC_URL:-}

    # HEALTHCHECK (Optional)
    HEALTHCHECK_PROVIDER="None"
    UPTIMEKUMA_PUSH_URL="" 
    HEALTHCHECKSIO_PING_URL=""

    # RAILWAY PROVIDED VARIABLES
    RAILWAY_STATIC_URL="" # Leave empty for default value

    ```
FROM python:alpine

WORKDIR /app

COPY ./ /app/

ARG PORT='' \
    API_USER= '' \
    API_PASS='' \
    # IF YOU WANT TO USE OWN REDIS SERVER, set it to 'true'
    CREATE_REDIS='false' \
    # IF YOU WANT LOG IP addresses, set it to 'true'
    LOG_REQUEST='false' \
    # OPTIONAL 
    REMEMBER_ME_TOKEN='' \
    JDB_SESSION='' \
    TIMEZONE='UTC' \
    IPINFO_TOKEN='' \
    INACTIVITY_TIMEOUT='' \
    REDIS_URL='' \
    # RAILWAY PROVIDED VARIABLES 
    RAILWAY_STATIC_URL='' \
    # NOT USABLE FOR NOW 
    CAPTCHA_SOLVER_URL='' \
    JAVDB_EMAIL='' \
    JAVDB_PASSWORD='' \
    # HEALTHCHECK (Optional)
    HEALTHCHECK_PROVIDER='None' \
    UPTIMEKUMA_PUSH_URL='' \
    HEALTHCHECKSIO_PING_URL=''

RUN apk --no-cache add alpine-conf bash && \
    setup-timezone -z "$TIMEZONE" && \
    apk del alpine-conf
    
RUN apk add --no-cache --virtual .build wget libffi-dev linux-headers musl-dev gcc build-base curl jq libxml2-dev libxslt-dev && \
    chmod +x install.sh && bash /app/install.sh && \
    pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r conf/requirements.txt

RUN apk del .build .rust_ext || apk del .build
RUN apk del .pillow_ext || echo

# MKDocs Static Site Generator
RUN pip install --no-cache-dir mkdocs-material && \
    mkdocs build -f /app/conf/mkdocs.yml && \
    pip uninstall mkdocs-material -y

RUN python -m compileall .

ENTRYPOINT ["bash", "start.sh"] 

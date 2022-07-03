# Build
FROM python:alpine as build
ENV COMMON_DEPS='libffi-dev linux-headers musl-dev gcc build-base libxml2-dev libxslt-dev' \
    PILLOW_DEPS='freetype-dev fribidi-dev harfbuzz-dev jpeg-dev lcms2-dev libimagequant-dev openjpeg-dev tcl-dev tiff-dev tk-dev zlib-dev' \
    WATCHFILES_DEPS='rust cargo'

WORKDIR /app
COPY conf/requirements.txt /app/

# Build deps, wheels and store
RUN apk add --no-cache $COMMON_DEPS $PILLOW_DEPS $WATCHFILES_DEPS
RUN pip install -U pip wheel setuptools && \
    pip wheel --wheel-dir=/app/wheels -r requirements.txt

# Release
FROM python:alpine
WORKDIR /app
COPY ./ /app/
ENV RUNTIME_DEPS='wget curl jq tmux ca-certificates'
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

COPY --from=build /app/wheels /app/wheels

RUN apk --no-cache add alpine-conf bash && \
    setup-timezone -z "$TIMEZONE" && \
    apk del alpine-conf
    
RUN apk add --no-cache $RUNTIME_DEPS && \
    chmod +x install.sh && bash /app/install.sh && \
    pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir --no-index --find-links=/app/wheels -r requirements.txt

# MKDocs Static Site Generator
RUN mkdocs build -f /app/conf/mkdocs.yml && \
    pip uninstall mkdocs-material -y

RUN python -m compileall .

ENTRYPOINT ["bash", "start.sh"] 

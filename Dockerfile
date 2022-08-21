# Release
FROM python:alpine
WORKDIR /app
COPY ./ /app/
ENV RUNTIME_DEPS="wget curl jq tmux ca-certificates"
ARG PORT \
    API_USER \
    API_PASS \
    CAPTCHA_SOLVER_URL \
    JAVDB_EMAIL \
    JAVDB_PASSWORD \
    CREATE_REDIS="false" \
    LOG_REQUEST="false" \
    REMEMBER_ME_TOKEN \
    JDB_SESSION \
    TIMEZONE="UTC" \
    IPINFO_TOKEN \
    INACTIVITY_TIMEOUT \
    REDIS_URL \
    RAILWAY_STATIC_URL \
    HEALTHCHECK_PROVIDER="None" \
    UPTIMEKUMA_PUSH_URL \
    HEALTHCHECKSIO_PING_URL \
    PLATFORM

COPY --from=iamrony777/javinfo-api:build-layer /app/wheels /app/wheels

RUN apk --no-cache add alpine-conf bash && \
    setup-timezone -z "$TIMEZONE" && \
    apk del alpine-conf
    
RUN apk add --no-cache $RUNTIME_DEPS && \
    chmod +x install.sh && bash /app/install.sh && \
    pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir --no-index --find-links=/app/wheels -r conf/requirements.txt

# MKDocs Static Site Generator
RUN mkdocs build -f /app/conf/mkdocs.yml && \
    pip uninstall mkdocs-material -y

RUN python -m compileall .

CMD ["bash", "start.sh"] 

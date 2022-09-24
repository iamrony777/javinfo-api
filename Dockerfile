# Release
FROM python:alpine
VOLUME [ "/data" ]
WORKDIR /app
COPY ./ /app/

ARG CREATE_REDIS \
    PLATFORM

ARG APP_NAME \
    RAILWAY_STATIC_URL \
    RENDER_EXTERNAL_URL

ENV RUNTIME_DEPS="curl jq tmux ca-certificates alpine-conf bash"

ENV PYTHONPATH=. \
    PLATFORM=$PLATFORM \
    OVERMIND_NO_PORT=1 \
    PORT=8000 \
    API_USER=admin \
    API_PASS=admin \
    CAPTCHA_SOLVER_URL=$CAPTCHA_SOLVER_URL \
    JAVDB_EMAIL=$JAVDB_EMAIL \
    JAVDB_PASSWORD=$JAVDB_PASSWORD \
    CREATE_REDIS=${CREATE_REDIS:-false} \
    LOG_REQUEST=${LOG_REQUEST:-false} \
    REMEMBER_ME_TOKEN=$REMEMBER_ME_TOKEN \
    JDB_SESSION=$JDB_SESSION \
    TZ=UTC \
    IPINFO_TOKEN=$IPINFO_TOKEN \
    INACTIVITY_TIMEOUT=300 \
    REDIS_URL=$REDIS_URL \
    BASE_URL=$BASE_URL \
    HEALTHCHECK_PROVIDER=$HEALTHCHECK_PROVIDER \
    UPTIMEKUMA_PUSH_URL=$UPTIMEKUMA_PUSH_URL \
    HEALTHCHECKSIO_PING_URL=$UPTIMEKUMA_PUSH_URL

# Ref. https://github.com/iamrony777/JavInfo-api/tree/build
COPY --from=iamrony777/javinfo-api:build-layer /app/wheels /app/wheels

RUN apk add --no-cache $RUNTIME_DEPS && \
    chmod +x install.sh && bash /app/install.sh && \
    pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir /app/wheels/*

# MKDocs Static Site Generator
RUN mkdocs build -f /app/conf/mkdocs.yml && \
    pip uninstall mkdocs-material -y

RUN python -m compileall .

EXPOSE ${PORT}
HEALTHCHECK --interval=5m --timeout=30s --start-period=5s --retries=5 CMD ["bash", "-c", "HEALTHCHECK_PROVIDER=local /app/api/scripts/ping.py"]

CMD [".", "/app/start.sh"] 

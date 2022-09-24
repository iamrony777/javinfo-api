FROM python:alpine AS prod

# VOLUME [ "/data" ]

WORKDIR /app

COPY ./ /app/

COPY --from=iamrony777/javinfo-api:build-layer /app/wheels /app/wheels

# Common (Required)
ARG CREATE_REDIS
ARG PLATFORM=container

# Optional , Platform based
ARG APP_NAME
ARG RAILWAY_STATIC_URL
ARG RENDER_EXTERNAL_URL

ENV RUNTIME_DEPS="curl jq tmux ca-certificates bash libjpeg" 

ENV PYTHONPATH=. \
    PLATFORM=${PLATFORM} \
    OVERMIND_NO_PORT=1 \
    PORT=8000 \
    API_USER=admin \
    API_PASS=admin \
    CREATE_REDIS=${CREATE_REDIS:-false} \
    LOG_REQUEST=${LOG_REQUEST:-false} \
    TZ=${TZ:-UTC} \
    INACTIVITY_TIMEOUT=300

RUN apk add --no-cache ${RUNTIME_DEPS} && \
    chmod +x install.sh && bash /app/install.sh && \
    pip install --no-cache-dir /app/wheels/* && \
    rm -rf /app/wheels && \
    python -m compileall -q .

RUN mkdocs build -f /app/conf/mkdocs.yml && \
    pip uninstall mkdocs-material -y

EXPOSE ${PORT}

HEALTHCHECK --interval=5m --timeout=30s --start-period=5s --retries=5 \
    CMD HEALTHCHECK_PROVIDER=local /app/api/scripts/ping.py

SHELL [ "/bin/bash", "-c" ]

CMD ["./start.sh"]

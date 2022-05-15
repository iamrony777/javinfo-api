FROM python:alpine3.15

WORKDIR /app

ARG JAVDB_EMAIL='' \
    JAVDB_PASSWORD='' \
    CAPTCHA_SOLVER_URL='' \
    API_USER='' \
    API_PASS='' \
    REDIS_URL=''

ADD ./ /app/

RUN apk --no-cache add alpine-conf && \
    setup-timezone -z Asia/Kolkata && \
    pip install -U pip setuptools wheel && \
    pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python", "main.py"] 

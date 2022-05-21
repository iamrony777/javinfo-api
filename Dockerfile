FROM python:alpine3.15

WORKDIR /app

ARG API_USER='' \
    API_PASS='' \
    REMEMBER_ME_TOKEN='' \
    JDB_SESSION='' \
    REDIS_URL='' \


    # NOT USABLE FOR NOW 
    CAPTCHA_SOLVER_URL='' \
    JAVDB_EMAIL='' \
    JAVDB_PASSWORD=''

ADD ./ /app/

RUN apk --no-cache add alpine-conf && \
    setup-timezone -z Asia/Kolkata && \
    pip install -U pip setuptools wheel && \
    pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python", "main.py"] 

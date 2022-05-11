FROM python:alpine3.15

WORKDIR /app

ARG DB_NAME='' \
    JAVDB_EMAIL='' \
    JAVDB_PASSWORD='' \
    MONGODB_URL='' \
    CAPTCHA_SOLVER_URL='' \
    API_USER='' \
    API_PASS=''

ADD ./ /app/

RUN apk --no-cache add alpine-conf && \
    setup-timezone -z Asia/Kolkata && \
    pip install -U pip setuptools wheel && \
    pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python", "main.py"] 

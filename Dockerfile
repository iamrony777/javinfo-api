FROM python:alpine3.15

WORKDIR /app

ARG DB_NAME='' \
    JAVDB_EMAIL='' \
    JAVDB_PASSWORD='' \
    MONGODB_URL='' \
    CAPTCHA_SOLVER_URL=''

ADD ./ /app/

RUN pip install -U pip setuptools wheel && \
    pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python", "main.py"] 

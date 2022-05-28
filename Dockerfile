FROM python:alpine3.15

WORKDIR /app

ADD ./ /app/

ARG PORT='' \
    API_USER='' \
    API_PASS='' 

# IF YOU WANT TO USE OWN REDIS SERVER, set it to 'true'   
ARG CREATE_REDIS='false'

# IF YOU WANT LOG IP addresses, set it to 'true'
ARG LOG_REQUEST='false'

# OPTIONAL 
ARG REMEMBER_ME_TOKEN='' \
    JDB_SESSION='' \
    TIMEZONE='UTC'

# NOT USABLE FOR NOW 
ARG CAPTCHA_SOLVER_URL='' \
    JAVDB_EMAIL='' \
    JAVDB_PASSWORD=''

    
RUN apk --no-cache add alpine-conf bash && \
    setup-timezone -z "$TIMEZONE" && \
    apk del alpine-conf


RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# MKDocs Static Site Generator
RUN pip install mkdocs-material && \
    mkdocs build && \
    mkdir -p /app/site && \
    pip uninstall mkdocs-material -y

RUN chmod +x install.sh && \
    bash /app/install.sh

ENTRYPOINT ["bash", "start.sh"] 

# Pull base image.
FROM aarch64/python:3.5-alpine

RUN apk update && apk upgrade && \
    apk add --no-cache git

RUN git clone https://github.com/benhoyle/website.git

WORKDIR /website

RUN mkdir instance

RUN pip install -r requirements.txt

RUN pip install --editable .

VOLUME data:./instance/

CMD  gunicorn \
    -b :8001 \
    --access-logfile - \
    --reload \
    "benhoyle.app:create_app()" \


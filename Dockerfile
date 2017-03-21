# Pull base image.
FROM aarch64/python:3.5-alpine

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

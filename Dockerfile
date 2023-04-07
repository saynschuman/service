FROM python:3.8.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD ./requirements.txt /code/

RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

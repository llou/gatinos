FROM python:3.11.4-slim-buster as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-traditional

RUN pip install --upgrade pip
RUN pip install flake8==6.0.0
COPY . /usr/src/app
#RUN flake8 --ignore=E501,F401 .


COPY requirements.txt requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt 

# -------------------------------------------------------------------------

FROM python:3.11.4-slim-buster

RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME

RUN apt-get update && apt-get install -yh --no-install-recommends netcat sed
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# es_ES.UTF-8 UTF-8/es_ES.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen es_ES.UTF-8

ENV LANG es_ES.UTF-8  
ENV LANGUAGE es_ES:es
ENV LC_ALL es_ES.UTF-8  

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

COPY . $APP_HOME
RUN chown -R app:app $APP_HOME

USER app
ENTRYPOINT ["/home/app/web/entrypoint.sh"]

# vim: ft=dockerfile

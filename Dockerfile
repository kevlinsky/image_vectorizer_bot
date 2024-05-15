FROM python:3.10.2

ENV PYTHONUNBUFFERED=1

RUN mkdir /image_vectorizer_bot
WORKDIR /image_vectorizer_bot

COPY requirements.txt /image_vectorizer_bot/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /image_vectorizer_bot/

FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
WORKDIR /config
RUN apt-get update
ADD requirements.txt /config/
RUN pip install -r requirements.txt
RUN mkdir /src;  
WORKDIR /src
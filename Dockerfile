#USING python:3-slim as base image to reduce size
FROM python:3-slim

# install google chrome
RUN apt-get -y update && \
    apt-get install -y \
    gnupg2 \
    wget \
    unzip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /tmp
RUN apt install -y /tmp/google-chrome-stable_current_amd64.deb
RUN sh -c 'rm -rf /tmp/* && google-chrome --version'

# # install chromedriver
# apt-get install -yqq unzip  && \
# wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && \
# unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ $$ \
# rm -rf /tmp/chromedriver.zip && \
# # upgrade pip,# install selenium
# pip install --upgrade pip && \
# pip install selenium && \
# pip install requests

# set display port to avoid crash
ENV DISPLAY=:99

# copy app/run.py file from local
COPY app/run.py /run.py
RUN sh -c 'head -n 30 /run.py'

#build docker: docker build -t milan-chrome-img:latest .
#tag: docker tag milan-img liulirun/milan-img
#push: docker image push liulirun/milan-img:latest
#DEBUG: https://stackoverflow.com/questions/26220957/how-can-i-inspect-the-file-system-of-a-failed-docker-build
#DEBUG: docker run --rm 00f017a8c2a6 cat /tmp/foo.txt
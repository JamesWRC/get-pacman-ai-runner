# Import arm32v6/debian:buster for R-Pi compatible images.
# FROM arm64v7/ubuntu:bionic 32 bit arm cpus
FROM arm64v8/ubuntu:latest
LABEL maintainer="github.com/JamesWRC"
ENV DEBIAN_FRONTEND=noninteractive

#   Update system.
RUN apt -y update
RUN apt -y upgrade

RUN apt-get -y install apt-transport-https ca-certificates curl gnupg2 software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository "deb [arch=arm64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"

RUN apt-get update
RUN apt-get -y install docker-ce
RUN bash service docker start
RUN docker run hello-world
RUN apk add docker

COPY setupAndRun.py /codebase/setupAndRun.py
RUN chmod +x /codebase/setupAndRun.py

# RUN addgroup runner
# RUN useradd pacman -u 1337 --groups runner --create-home

# USER pacman

CMD ["python3 /codebase/setupAndRun.py"]


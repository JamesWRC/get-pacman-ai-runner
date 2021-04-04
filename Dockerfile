# Import arm32v6/debian:buster for R-Pi compatible images.
# FROM arm64v7/ubuntu:bionic 32 bit arm cpus
FROM arm64v8/ubuntu:latest
LABEL maintainer="github.com/JamesWRC"
ENV DEBIAN_FRONTEND=noninteractive

#   Update system.
RUN apt -y update
RUN apt -y upgrade
RUN apt-get -y install apt-transport-https ca-certificates curl gnupg2 lsb-release software-properties-common git

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# RUN add-apt-repository "deb [arch=arm64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
RUN echo \
  "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null 

RUN apt-get update

RUN apt-get -y install docker-ce docker-ce-cli containerd.io
RUN bash service docker start
# RUN docker run hello-world

RUN mkdir /assets
COPY setupAndRun.py /assets/setupAndRun.py
RUN chmod +x /assets/setupAndRun.py

# RUN addgroup runner
# RUN useradd pacman -u 1337 --groups runner --create-home

# USER pacman

CMD ["python3 /assets/setupAndRun.py"]


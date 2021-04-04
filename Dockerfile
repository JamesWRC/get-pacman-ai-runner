# Import arm32v6/debian:buster for R-Pi compatible images.
# FROM arm64v7/ubuntu:bionic 32 bit arm cpus
FROM arm64v8/ubuntu:latest
LABEL maintainer="github.com/JamesWRC"
ENV DEBIAN_FRONTEND=noninteractive

#   Update system.
RUN apt -y update
RUN apt -y upgrade

RUN apk add docker

COPY setupAndRun.py /codebase/setupAndRun.py
RUN chmod +x /codebase/setupAndRun.py

# RUN addgroup runner
# RUN useradd pacman -u 1337 --groups runner --create-home

# USER pacman

CMD ["python3 /codebase/setupAndRun.py"]


FROM ubuntu:22.04

# setting up os env
USER root
WORKDIR /home/nonroot/devika
RUN groupadd -r nonroot && useradd -r -g nonroot -d /home/nonroot/devika -s /bin/bash nonroot

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

# setting up python3
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential software-properties-common curl sudo wget git
RUN apt-get install -y python3 python3-pip python3-venv

# copy devika python engine only
COPY devika /home/nonroot/devika/devika
COPY config.toml /home/nonroot/devika/
COPY main.py /home/nonroot/devika/
COPY pyproject.toml /home/nonroot/devika/
RUN chown -R nonroot:nonroot /home/nonroot/devika
RUN python3 -m venv .venv && . .venv/bin/activate
RUN pip install .

USER nonroot
WORKDIR /home/nonroot/devika
ENV PATH="/home/nonroot/devika/.venv/bin:$HOME/.cargo/bin:$PATH"
RUN mkdir /home/nonroot/devika/db

ENTRYPOINT [ "python3", "-m", "main" ]

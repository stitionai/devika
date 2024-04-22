FROM debian:12

# setting up os env
USER root
WORKDIR /home/nonroot/angelic
RUN groupadd -r nonroot && useradd -r -g nonroot -d /home/nonroot/angelic -s /bin/bash nonroot

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# setting up python3
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential software-properties-common curl sudo wget git
RUN apt-get install -y python3 python3-pip
RUN curl -fsSL https://astral.sh/uv/install.sh | sudo -E bash -
RUN $HOME/.cargo/bin/uv venv
ENV PATH="/home/nonroot/angelic/.venv/bin:$HOME/.cargo/bin:$PATH"

# copy angelic python engine only
RUN $HOME/.cargo/bin/uv venv
COPY requirements.txt /home/nonroot/angelic/
RUN UV_HTTP_TIMEOUT=100000 $HOME/.cargo/bin/uv pip install -r requirements.txt 
RUN playwright install --with-deps

COPY src /home/nonroot/angelic/src
COPY config.toml /home/nonroot/angelic/
COPY angelic.py /home/nonroot/angelic/
RUN chown -R nonroot:nonroot /home/nonroot/angelic

USER nonroot
WORKDIR /home/nonroot/angelic
ENV PATH="/home/nonroot/angelic/.venv/bin:$HOME/.cargo/bin:$PATH"
RUN mkdir /home/nonroot/angelic/db

ENTRYPOINT [ "python3", "-m", "angelic" ]

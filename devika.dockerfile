FROM debian:12

# setting up os env
USER root
WORKDIR /home/nonroot/devika
RUN groupadd -r nonroot && useradd -r -g nonroot -d /home/nonroot/devika -s /bin/bash nonroot

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# setting up python3
RUN apt-get update && apt-get upgrade
RUN apt-get install -y build-essential software-properties-common curl sudo wget
RUN apt-get install -y python3 python3-pip
RUN curl -fsSL https://astral.sh/uv/install.sh | sudo -E bash -
RUN export PATH=$PATH:$HOME/.cargo/bin
RUN echo $PATH
RUN $HOME/.cargo/bin/uv venv
RUN python3 -V && pip3 -V

# copy devika python engine only
COPY requirements.txt /home/nonroot/devika/
RUN $HOME/.cargo/bin/uv pip install -r requirements.txt 
RUN $HOME/.cargo/bin/uv pip install flask flask-cors

COPY src /home/nonroot/devika/src
COPY config.toml /home/nonroot/devika/
COPY devika.py /home/nonroot/devika/
RUN ls

RUN chown -R nonroot:nonroot /home/nonroot/devika
USER nonroot

WORKDIR /home/nonroot/devika

ENTRYPOINT [ "python3", "devika.py" ]
FROM debian:12

# setting up os env
USER root
WORKDIR /home/nonroot/client
RUN groupadd -r nonroot && useradd -r -g nonroot -d /home/nonroot/client -s /bin/bash nonroot

# install node js 
RUN apt-get update && apt-get upgrade
RUN apt-get install -y build-essential software-properties-common curl sudo wget
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
RUN apt-get install nodejs

# copying devika app client only
COPY ui /home/nonroot/client/
COPY src /home/nonroot/client/
COPY config.toml /home/nonroot/client/

RUN npm install && npm upgrade
RUN chown -R nonroot:nonroot /home/nonroot/client

USER nonroot
WORKDIR /home/nonroot/client

ENTRYPOINT [ "npm", "run", "dev" ]
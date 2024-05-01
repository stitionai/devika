FROM node:18.20.2-bullseye

# setting up build variable
ARG vite_api_base_url
ARG user
ARG uid
ARG debug
ARG dev_mode
ARG apt_cache_dir=/var/cache/apt

ENV VITE_API_BASE_URL=${vite_api_base_url}
ENV DEBUG="$debug"
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root/webui

RUN --mount=type=cache,target=${apt_cache_dir},sharing=locked \
    if [ -n "${debug}" ]; then set -eux; fi && \
    apt-get -q update > /dev/null && \
    if [ -z "${dev_mode}" ]; then apt-get -qy upgrade > /dev/null; fi && \
    apt-get install -qy build-essential software-properties-common curl wget git > /dev/null

COPY ui ui
COPY src src
COPY config.toml .

ARG npm_cache_dir=/var/cache/npm

WORKDIR /root/webui/ui

RUN --mount=type=cache,target=${npm_cache_dir},sharing=locked \
    npm config set --global cache "${npm_cache_dir}" && \
    npm install -g npm@latest > /dev/null && \
    yarn install --frozen-lockfile > /dev/null 

ENTRYPOINT [ "yarn", "run", "dev", "--host" ]
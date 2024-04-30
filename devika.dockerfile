FROM python:3.11.9-bookworm as backend

ARG root_dir

WORKDIR "${root_dir}"

ARG debug
ARG dev_mode
ARG apt_cache_dir=/var/cache/apt

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBUG="$debug"
ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES=all

RUN --mount=type=cache,target=${apt_cache_dir},sharing=locked \
    if [ -n "${debug}" ]; then set -eux; fi && \
    apt-get update && \
    if [ -z "${dev_mode}" ]; then apt-get -qy upgrade > /dev/null; fi && \
    apt-get install -y --no-install-recommends software-properties-common \
      curl wget git

ADD --checksum=sha256:4da8dde69eca0d9bc31420349a204851bfa2a1c87aeb87fe0c05517797edaac4 https://repo.anaconda.com/miniconda/Miniconda3-py311_24.3.0-0-Linux-x86_64.sh /tmp/

ARG conda_root=/var/miniconda3
ARG venv_name=devika_env

ENV CONDA_ROOT="${conda_root}"
ENV VENV_NAME="${venv_name}"
ENV APP_ROOT="${root_dir}"

RUN if [ -n "${debug}" ]; then set -eux; fi && \
    echo "Installing Miniconda..." && \
    mkdir -p "${CONDA_ROOT}" && \
    bash /tmp/Miniconda3-py311_24.3.0-0-Linux-x86_64.sh -b -u -p ${CONDA_ROOT} > /dev/null

ARG user=root
ARG uid
ARG conda_pkgs_dir="${CONDA_ROOT}/pkgs"

ENV PATH="/home/${user}/.local/bin:${CONDA_ROOT}/bin:${PATH}"
ENV PYTHONPATH="${root_dir}/devika"

WORKDIR ${APP_ROOT}

COPY environment.yml .

RUN --mount=type=cache,target=${conda_pkgs_dir},sharing=locked \
    if [ -n "${debug}" ]; then set -eux; fi && \
    conda config --add channels conda  && \
    conda config --add channels conda-forge  && \
    conda config --add channels anaconda  && \
    conda config --add channels microsoft  && \
    conda install -qy pip && \
    conda env create --file environment.yml -n "${venv_name}" && \
    conda run -n "${venv_name}" playwright install-deps chromium

COPY src src
COPY sample.config.toml .
COPY devika.py .
COPY entrypoint.sh /docker-entrypoint.sh

# Patch source files for Docker environment
RUN if [ -n "${debug}" ]; then set -eux; fi && \
    chmod a+x /docker-entrypoint.sh && \
    sed -i 's#OLLAMA = "http://127.0.0.1:11434"#OLLAMA = "OLLAMA_API_ENDPOINT"#' sample.config.toml && \
    echo "import os" | cat - src/llm/ollama_client.py > temp_file && mv -f temp_file src/llm/ollama_client.py && \
    sed -i 's#Config().get_ollama_api_endpoint()#os.getenv(Config().get_ollama_api_endpoint())#g' src/llm/ollama_client.py

ENTRYPOINT [ "/docker-entrypoint.sh" ]

# Activate Miniconda environment
RUN eval "$(conda shell.bash activate "$venv_name")"
# Make RUN commands use the new environment
SHELL [ "conda", "run", "-n $venv_name /bin/bash -c" ]

CMD [ "python3", "-m", "devika" ]

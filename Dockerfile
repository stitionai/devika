FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    nginx \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm \
    && curl https://bun.sh/install | bash

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN git clone https://github.com/stitionai/devika.git

WORKDIR /devika

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN cd /devika \
    && /root/.cargo/bin/uv venv \
    && pip install -r /devika/requirements.txt \
    && playwright install --with-deps
# Install Bun dependencies for the UI
WORKDIR /devika/ui
RUN /root/.bun/bin/bun install

# Expose the port 3000 from the container to port 3001 on the host
#EXPOSE 3000:3001

RUN echo '#!/bin/bash\n\
if [ -f /devika/.env ]; then\n\
  export $(cat /devika/.env | grep -v '^#' | xargs)\n\
fi\n\
API_JS_PATH="/devika/ui/src/lib"\n\
if [ -f .env ]; then\n\
  export $(grep -v '^#' /devika/.env | xargs)\n\
fi\n\
service nginx restart\n\
cd /devika \n\
/root/.cargo/bin/uv venv && pip install -r /devika/requirements.txt && playwright install --with-deps && python3 /devika/devika.py &\n\
cd /devika/ui && /root/.bun/bin/bun run dev --host\n' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]

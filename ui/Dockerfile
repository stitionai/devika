FROM debian:bookworm-slim AS build

RUN apt-get update && apt-get install -y curl ca-certificates unzip
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"
WORKDIR /app
COPY package.json .
RUN bun install
COPY . .
RUN bun run build
EXPOSE 3000
CMD ["bun", "run", "dev", "--host"]
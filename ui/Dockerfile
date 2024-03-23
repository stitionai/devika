FROM debian:bookworm-slim AS build

RUN apt-get update && apt-get install -y curl ca-certificates unzip
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"
ENV API_BASE_URL=http://devika-python:1337
WORKDIR /app
COPY . .
RUN bun install
RUN bun run build
EXPOSE 3000
CMD ["bun", "run", "dev", "--host"]
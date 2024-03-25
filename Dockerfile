FROM oven/bun:1 as base

WORKDIR /build
COPY ui/package*.json .
RUN rm -rf node_modules
RUN rm -rf build
COPY ui/. .
RUN bun install
RUN bun run build

# Thanks https://stackoverflow.com/q/76988450

FROM python:3.10-slim

WORKDIR /app
RUN apt update
RUN apt install git -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY --from=0 /build/build /app/ui/build
COPY src /app/src
COPY config.toml config.toml
COPY devika.py /app/devika.py
COPY src .

EXPOSE 1337

CMD [ "python3", "devika.py"]
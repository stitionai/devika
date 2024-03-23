FROM python:3.10-slim
RUN apt-get update
RUN apt-get install -y git
RUN pip install uv
RUN uv venv
COPY requirements.txt .
RUN uv pip install -r requirements.txt
COPY . .
RUN playwright install --with-deps
EXPOSE 1337
CMD [ "python3", "devika.py"]
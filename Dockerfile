FROM python:3.10-slim
RUN apt-get update
RUN apt-get install -y git
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install playwright
RUN playwright install --with-deps
EXPOSE 1337
CMD [ "python3", "devika.py"]
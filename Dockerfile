FROM nikolaik/python-nodejs:python3.11-nodejs22-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app/
COPY . /app/

RUN pip3 install --no-cache-dir -U -r requirements.txt

CMD ["bash", "start"]
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && pip install --no-cache-dir appworld==0.1.3.post1 \
    && appworld install \
    && apt-get purge -y gcc libc6-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /appworld
RUN appworld download data --root /appworld

COPY aw_client.py /opt/aw_client.py

EXPOSE 9000
CMD ["appworld", "serve", "environment", "--port", "9000", "--no-show-usage", "--root", "/appworld"]

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && pip install --no-cache-dir appworld==0.1.3.post1 \
    && appworld install \
    && apt-get purge -y gcc libc6-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /appworld
# Download and checksum the data bundle before unpacking it with appworld's own
# bundle reader, so the image can only ever build on the pinned data release.
COPY download_data.py /opt/download_data.py
RUN python /opt/download_data.py /appworld/.tmp/data-0.1.0.bundle \
    && python -c "from appworld.common.constants import PASSWORD, SALT; \
from appworld.common.utils import unpack_bundle; \
unpack_bundle(bundle_file_path='/appworld/.tmp/data-0.1.0.bundle', \
base_directory='/appworld', password=PASSWORD, salt=SALT)" \
    && rm -rf /appworld/.tmp

COPY aw_client.py /opt/aw_client.py

EXPOSE 9000
CMD ["appworld", "serve", "environment", "--port", "9000", "--no-show-usage", "--root", "/appworld"]

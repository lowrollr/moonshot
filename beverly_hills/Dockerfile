FROM python:3.8-slim-buster
WORKDIR /code
COPY requirements.txt .
RUN apt-get update && apt-get install --no-install-recommends wget libopenblas-dev cmake build-essential automake python-dev gcc g++ subversion -y \
  && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install -r requirements.txt --no-cache-dir 
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr --build=unknown-unknown-linux && \
  make && \
  make install
RUN python3 -m pip install ta-lib && rm -R ta-lib ta-lib-0.4.0-src.tar.gz
COPY src .
RUN chmod +x wait-for-it.sh
CMD ["./wait-for-it.sh", "main_data_consumer:9090", "-t", "0", "--", "python", "main.py"]

  
FROM python:3.8-slim-buster
WORKDIR /code
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir
RUN python3 -m pip install tensorflow --no-cache-dir
RUN apt-get update && apt-get install --no-install-recommends wget build-essential python-dev -y \
  && rm -rf /var/lib/apt/lists/* 
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
RUN python3 -m pip install ta-lib && rm -R ta-lib ta-lib-0.4.0-src.tar.gz
COPY src .
RUN chmod +x wait-for-it.sh
CMD ["./wait-for-it.sh", "main_data_consumer:9090", "-t", "0", "--", "python", "main.py"]

FROM python:3.8-slim-buster
WORKDIR /code
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir
COPY src .
RUN chmod +x wait-for-it.sh
CMD ["./wait-for-it.sh", "main_data_consumer:9090", "-t", "0", "--", "python", "main.py"]

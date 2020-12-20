FROM python:3.8-slim-buster
WORKDIR /code
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir
COPY src .
CMD ["python", "main.py"]
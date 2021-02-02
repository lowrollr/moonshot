FROM python:3.8

ENV VAR1 10

WORKDIR /dashboard

COPY requirements.txt /
RUN pip install  -r  /requirements.txt
COPY ./  ./

CMD ["python", "./start.py"]
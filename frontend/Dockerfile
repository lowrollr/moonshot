FROM python:3.8

WORKDIR /dashboard

COPY requirements.txt /
RUN pip install  -r  /requirements.txt
COPY .  .
RUN chmod +x wait-for-it.sh

CMD ["./wait-for-it.sh", "portfolio_manager:8000", "-t", "0", "--", "python", "./dashboard/app.py"]

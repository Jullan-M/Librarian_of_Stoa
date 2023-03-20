FROM python:3.8
COPY main.py utilities.py .env ./
COPY cogs/*.py cogs/
COPY books/*.json books/
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "-u", "./main.py"]
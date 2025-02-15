FROM python:3.12.3
COPY main.py utilities.py ./
COPY cogs/*.py cogs/
COPY books/*.json books/
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "-u", "./main.py"]
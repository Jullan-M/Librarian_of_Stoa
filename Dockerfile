FROM python:3.8
#WORKDIR /Librarian_of_Stoa
COPY main.py utilities.py .env ./
COPY cogs/ cogs/
COPY books/ books/
COPY requirements.txt .
RUN pip install -r requirements.txt
#ENV PYTHONPATH /Librarian_of_Stoa
CMD ["python", "-u", "./main.py"]
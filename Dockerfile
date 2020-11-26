FROM python:3.7

COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install openjdk-11-jdk -y && \
    python -m pip install -r requirements.txt && \
    python -m pip install --upgrade git+https://github.com/terrier-org/pyterrier.git#egg=python-terrier

COPY . .

ENTRYPOINT python3 app.py
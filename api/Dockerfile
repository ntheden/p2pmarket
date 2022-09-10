FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY main.py logging.conf app/

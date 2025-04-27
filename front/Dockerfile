FROM python:3.11-slim

WORKDIR /app

COPY ./front ./front
COPY requirments-front.txt .

RUN pip install --upgrade pip
RUN pip install -r requirments-front.txt

CMD ["python3", "front/main.py"]

FROM python:3.11-slim

WORKDIR /app

COPY ./back ./back
COPY ./tests ./tests
COPY requirments-back.txt .

RUN pip install --upgrade pip
RUN pip install -r requirments-back.txt

EXPOSE 9000

CMD ["uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "9000"]

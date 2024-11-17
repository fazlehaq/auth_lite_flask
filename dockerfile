FROM python:3.9-slim

WORKDIR /app

COPY . /app


ARG DB_PATH
ENV DB_PATH=$DB_PATH

RUN pip install -r requirements.txt
RUN python init_db.py

EXPOSE 5000

CMD ["python", "app.py"]

FROM python:3.13.0rc2-slim
WORKDIR /etl

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD sleep 60 && python main.py
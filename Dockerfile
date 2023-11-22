FROM python:alpine3.18

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000
CMD ["python", "app.py"]
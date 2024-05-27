FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/usr/src/app"

EXPOSE 5002

CMD ["python", "main.py"]

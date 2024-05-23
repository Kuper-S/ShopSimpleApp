FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY .. . 

EXPOSE 8000

# Run client_web_server.py when the container launches
CMD ["python", "client_web_server.py"]

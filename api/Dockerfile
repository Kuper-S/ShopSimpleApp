FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

EXPOSE 5000

# Run insert_data.py and then api_server.py when the container launches
CMD ["sh", "-c", "python insert_data.py && python api_server.py"]

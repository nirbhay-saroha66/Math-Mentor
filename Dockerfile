FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
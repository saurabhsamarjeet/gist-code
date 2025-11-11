FROM python:3.10-slim

WORKDIR /app

# Copy requirements file first (for caching)
COPY requirements.txt .

# Install dependencies (including Flask and Gunicorn)
RUN pip install -r requirements.txt

# Copy rest of your code
COPY . .

# Expose the port Flask/Gunicorn will use
EXPOSE 8080

# Start using Gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080"]


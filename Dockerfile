# Use the official Python runtime image
FROM python:3.12.3-slim  

# Set environment variables 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Set the working directory (automatically creates the dir)
WORKDIR /app

# Install system dependencies if needed (e.g., for psycopg2 or pillow)
# RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Django project
COPY . /app/

# Expose the Django port
EXPOSE 8000

# Run using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "crawler.wsgi:application"]
# Base image
FROM python:3.13-alpine@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/dev.txt

# Copy project files
COPY . .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

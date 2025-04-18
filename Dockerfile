# Base image
FROM python:3.13-alpine@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG APP_ENV=dev
ENV APP_ENV=${APP_ENV}

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/${APP_ENV}.txt

# Copy project files
COPY . .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput

# Run Migrations
RUN python manage.py makemigrations && python manage.py migrate

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

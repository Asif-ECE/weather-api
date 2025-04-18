![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# Travel Weather Recommendation API

A Django RESTful API that helps travelers choose the best districts in Bangladesh to visit based on weather and air quality conditions using real-time data from Open-Meteo.

---

## Features

- 🔐 JWT-authenticated endpoints (via SimpleJWT)
- 🌎 Fetches and analyzes real-time temperature and PM2.5 air quality
- 🏙️ Ranks top 10 districts to visit based on best 2 PM weather and air quality
- 🧭 Travel recommendation comparing your current location and desired destination
- ⚡ Caching and retry mechanisms for reliable API calls

---

## Project Structure

WeatherAPI
├── Dockerfile
├── accounts
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config
│   ├── asgi.py
│   ├── django
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── test.py
│   ├── env.py
│   ├── settings
│   │   └── simple_jwt.py
│   ├── urls.py
│   └── wsgi.py
├── core
│   ├── admin.py
│   ├── apps.py
│   ├── management
│   │   └── commands
│   │       └── fetch_json.py
│   ├── migrations
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── docker-compose.yml
├── manage.py
├── readme.md
├── requirements
│   ├── base.txt
│   ├── dev.txt
│   ├── prod.txt
│   └── test.txt
└── utils
    ├── district_data_loader.py
    ├── message_generator.py
    └── openmateo_client.py

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Asif-ECE/weather-api.git
cd weather-api
```

### 2. Create and configure .env
> Note: Use the .env.example file as a reference for setting up your own environment. The main .env file is included in this project since it's intended for illustration purposes only and won't be deployed to production.

```bash
DJANGO_SETTINGS_MODULE='config.django.dev'          #   .dev | .prod | .test
DJANGO_DEBUG=True
SECRET_KEY=secret-key
ALLOWED_HOSTS=*
DISTRICT_DATA_URL='data-source-url-endpoint'
```

### 3. Run Project

#### Option 1: Build and Run with Docker

```bash
docker-compose up --build
```

#### Option 2. Run Locally (Manual Setup)

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/test.txt    # Options: test.txt, dev.txt, prod.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

## API Endpoints

| Endpoint                             | Method | Auth | Description                                                             |
|--------------------------------------|--------|------|-------------------------------------------------------------------------|
| `/api/core/best-cities-to-visit/`   | GET    | ✅   | Get top 10 districts to visit based on weather temperature and air quality.           |
| `/api/core/travel-recommendation/`  | GET    | ✅   | Recommend travel plan comparing source and destination weather.        |
| `/api/auth/signup/`                 | POST   | ❌   | Sign up as a new user.                                                 |
| `/api/auth/login/`                  | POST   | ❌   | Login as an existing user.                                             |
| `/api/auth/refresh/`                | POST   | ❌   | Refresh access token.                                                  |
| `/api/auth/logout/`                 | POST   | ✅   | Logout from system.                                                    |

> **Example**
> `/api/core/travel-recommendation/?destination=faridpur&lat=29.89&long=50.21&date=2025-04-20`

> Note: This project keeps authentication simple. Features like profile updates, password resets, etc., are intentionally excluded.

## Docker Details

### Dockerfile
- Base Image: Uses the lightweight python:3.13-alpine image for smaller build size and security.
- Environment Setup: Configures Django-specific environment variables and working directory.
- Dependency Management: Installs Python dependencies from requirements/<APP_ENV>.txt, where APP_ENV is passed from the .env file to customize the environment (dev, prod, or test).
- Application Binding: Exposes the Django app on 0.0.0.0:8000 to make it accessible from outside the container.
- Startup Command: Uses CMD to run the development server via manage.py runserver.

### docker-compose.yml
- Service Definition: Orchestrates the Django web service using the Dockerfile in the project root.
- Port Mapping: Exposes container port 8000 to host port 8000, making the API accessible via http://localhost:8000.
- Environment Management: Loads environment variables from a .env file to configure Django settings, secrets, and runtime behavior.
- Live Reload Support: Mounts the local project directory into the container (volumes) to reflect code changes instantly without rebuilding.
- Command Override: Starts the Django development server via python manage.py runserver.

## External APIs Used

### This project users:
- Open-Meteo Weather API
- Open-Meteo Air Quality API

## Author
### Md. Asif Mostafa
Python, Django & Data Engineering Enthusiast
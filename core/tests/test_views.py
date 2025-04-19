import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta

User = get_user_model()

@pytest.mark.django_db
def test_unauthorized_access_to_top_districts():
    client = APIClient()
    response = client.get("/api/core/best-cities-to-visit/")
    assert response.status_code == 401


@pytest.fixture
def api_client_with_token(db):
    user = User.objects.create_user(username="testuser", password="testpass123")
    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@patch("core.views.get_districts")
@patch("core.views.get_top_districts_to_visit")
def test_top_districts_success(mock_top_districts, mock_get_districts, api_client_with_token):
    mock_get_districts.return_value = [
        {"name": "Dhaka", "lat": "23.8103", "long": "90.4125"},
        {"name": "Somewhere", "lat": "33.8103", "long": "83.4125"}
    ]
    mock_top_districts.return_value = [
        {"district_name": "Dhaka", "avg_temperature_2pm": 28.0, "avg_pm2_5": 40.0, "lat": "23.8103", "long": "90.4125"},
        {"district_name": "Somewhere", "avg_temperature_2pm": 33.0, "avg_pm2_5": 34.0, "lat": "33.8103", "long": "83.4125"}
    ]

    response = api_client_with_token.get("/api/core/best-cities-to-visit/")
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert response.data[0]["district_name"] == "Dhaka"


@patch("core.views.get_districts", side_effect=Exception("File not found"))
def test_top_districts_failure(mock_get_districts, api_client_with_token):
    response = api_client_with_token.get("/api/core/best-cities-to-visit/")
    assert response.status_code == 500
    assert response.data["success"] is False
    assert "Unable to load district data." in response.data["message"]


def test_travel_recommendation_missing_param(api_client_with_token):
    response = api_client_with_token.get("/api/core/travel-recommendation/", {
        "destination": "Dhaka"
    })
    assert response.status_code == 400
    assert "lat" in str(response.data)
    assert "long" in str(response.data)


@patch("core.views.get_districts")
@patch("core.views.compare_weather")
@patch("core.views.generate_weather_message")
def test_travel_recommendation_recommended(mock_message, mock_compare, mock_get_districts, api_client_with_token):
    mock_get_districts.return_value = [
        {"name": "Dhaka", "lat": "23.8103", "long": "90.4125"}
    ]
    mock_compare.return_value = {"temp_diff": -2, "air_con_diff": -5}
    mock_message.return_value = "Cool and clean air in Dhaka."

    travel_date = (date.today() + timedelta(days=3)).isoformat()
    response = api_client_with_token.get("/api/core/travel-recommendation/", {
        "destination": "Dhaka",
        "lat": 22.3569,
        "long": 91.7832,
        "date": travel_date
    })

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["recommendation"] == "Recommended"
    assert "Cool and clean air" in response.data["message"]


@patch("core.views.get_districts")
@patch("core.views.compare_weather")
@patch("core.views.generate_weather_message")
def test_travel_recommendation_not_recommended(mock_message, mock_compare, mock_get_districts, api_client_with_token):
    mock_get_districts.return_value = [{"name": "Dhaka", "lat": "23.8103", "long": "90.4125"}]
    mock_compare.return_value = {"temp_diff": 2, "air_con_diff": 5}
    mock_message.return_value = "Too hot and polluted."

    travel_date = (date.today() + timedelta(days=3)).isoformat()
    response = api_client_with_token.get("/api/core/travel-recommendation/", {
        "destination": "Dhaka",
        "lat": 22.3569,
        "long": 91.7832,
        "date": travel_date
    })

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["recommendation"] == "Not Recommended"


@patch("core.views.get_districts")
def test_travel_recommendation_district_not_found(mock_get_districts, api_client_with_token):
    mock_get_districts.return_value = [{"name": "Chittagong", "lat": "22.3569", "long": "91.7832"}]

    travel_date = (date.today() + timedelta(days=2)).isoformat()
    response = api_client_with_token.get("/api/core/travel-recommendation/", {
        "destination": "Nonexistent",
        "lat": 22.3569,
        "long": 91.7832,
        "date": travel_date
    })

    assert response.status_code == 400
    assert response.data["success"] is False
    assert "Destination 'Nonexistent' not found" in response.data["message"]


def test_travel_recommendation_invalid_date(api_client_with_token):
    response = api_client_with_token.get("/api/core/travel-recommendation/", {
        "destination": "Dhaka",
        "lat": 23.8103,
        "long": 90.4125,
        "date": (date.today() - timedelta(days=1)).isoformat()
    })

    assert response.status_code == 400
    assert "Travel date cannot be in the past" in str(response.data)


def test_travel_recommendation_date_beyond_limit(api_client_with_token):
    future_date = (date.today() + timedelta(days=20)).isoformat()
    response = api_client_with_token.get("/api/core/travel-recommendation/", {
        "destination": "Dhaka",
        "lat": 23.8103,
        "long": 90.4125,
        "date": future_date
    })
    assert response.status_code == 400
    assert "Travel date must be within 15 days" in str(response.data)

from datetime import date, timedelta
from core.serializers import TravelRecommendationQuerySerializer


def test_today_date():
    data = {
        "destination": "Dhaka",
        "lat": 23.81,
        "long": 90.41,
        "date": date.today().isoformat()
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert serializer.is_valid()

def test_15_days_future():
    data = {
        "destination": "Dhaka",
        "lat": 23.81,
        "long": 90.41,
        "date": (date.today() + timedelta(days=15)).isoformat()
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert serializer.is_valid()


def test_valid_travel_date():
    data = {
        "destination": "Dhaka",
        "lat": 23.8103,
        "long": 90.4125,
        "date": (date.today() + timedelta(days=5)).isoformat()
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert serializer.is_valid()


def test_invalid_past_date():
    data = {
        "destination": "Dhaka",
        "lat": 23.8103,
        "long": 90.4125,
        "date": (date.today() - timedelta(days=1)).isoformat()
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert not serializer.is_valid()
    assert "Travel date cannot be in the past." in str(serializer.errors)


def test_invalid_too_future_date():
    data = {
        "destination": "Dhaka",
        "lat": 23.8103,
        "long": 90.4125,
        "date": (date.today() + timedelta(days=20)).isoformat()
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert not serializer.is_valid()
    assert "Travel date must be within 15 days from today." in str(serializer.errors)


def test_invalid_lat_long():
    data = {
        "destination": "Dhaka",
        "lat": "abc",  # invalid
        "long": 90.4,
        "date": (date.today() + timedelta(days=1)).isoformat()
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert not serializer.is_valid()
    assert "lat" in serializer.errors


def test_missing_fields():
    data = {"lat": 23.8, "long": 90.4}
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert not serializer.is_valid()
    assert "destination" in serializer.errors
    assert "date" in serializer.errors


def test_empty_values():
    data = {
        "destination": "",
        "lat": None,
        "long": None,
        "date": ""
    }
    serializer = TravelRecommendationQuerySerializer(data=data)
    assert not serializer.is_valid()
    assert "destination" in serializer.errors
    assert "lat" in serializer.errors
    assert "long" in serializer.errors
    assert "date" in serializer.errors


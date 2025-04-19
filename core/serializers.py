from datetime import date, timedelta
from rest_framework import serializers


class DistrictAirWeatherSerializer(serializers.Serializer):
    """
    Serializer for representing average temperature and air quality data of a district.
    """
    district_name = serializers.CharField(help_text="Name of the district")
    avg_temperature_2pm = serializers.FloatField(help_text="Average temperature at 2PM")
    avg_pm2_5 = serializers.FloatField(help_text="Average PM2.5 air quality value")
    lat = serializers.CharField(help_text="Latitude of the district")
    long = serializers.CharField(help_text="Longitude of the district")


class TravelRecommendationQuerySerializer(serializers.Serializer):
    """
    Serializer for travel recommendation query params.
    """
    destination = serializers.CharField(help_text="Name of the destination district")
    lat = serializers.FloatField(help_text="Latitude of your current location")
    long = serializers.FloatField(help_text="Longitude of your current location")
    date = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        help_text="Travel date in YYYY-MM-DD format"
    )

    def validate_date(self, value):
        today = date.today()
        if value < today:
            raise serializers.ValidationError("Travel date cannot be in the past.")
        if value > (today + timedelta(days=15)):
            raise serializers.ValidationError("Travel date must be within 15 days from today.")
        return value
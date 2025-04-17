from datetime import date
from rest_framework import serializers


class DistrictAirWeatherSerializer(serializers.Serializer):
    district_name = serializers.CharField()
    avg_temperature_2pm = serializers.FloatField()
    avg_pm2_5 = serializers.FloatField()
    lat = serializers.CharField()
    long = serializers.CharField()


class TravelRecommendationQuerySerializer(serializers.Serializer):
    destination = serializers.CharField()
    lat = serializers.FloatField()
    long = serializers.FloatField()
    date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    def validate_date(self, value):
        today = date.today()
        if value < today:
            raise serializers.ValidationError("Travel date cannot be in the past.")
        if value > today.replace(day=min(today.day + 15, 28)):
            raise serializers.ValidationError("Travel date must be within 15 days from today.")
        return value